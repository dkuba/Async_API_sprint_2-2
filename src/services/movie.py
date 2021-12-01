from functools import lru_cache
from typing import List, Optional

import elasticsearch.exceptions
from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from models.movie import Movie

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class MovieService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, movie_id: str) -> Optional[Movie]:
        """Возвращает объект фильма. Он опционален, так как фильм может
        отсутствовать в базе.
        """
        movie = await self._movie_from_cache(movie_id)

        if not movie:
            movie = await self._get_movie_from_elastic(movie_id)
            if not movie:
                return None

            await self._put_movie_to_cache(movie)

        return movie

    async def _get_movie_from_elastic(self, movie_id: str) -> Optional[Movie]:
        try:
            doc = await self.elastic.get("movies", movie_id)
        except elasticsearch.exceptions.NotFoundError:
            return None

        return Movie(**doc["_source"])

    async def _movie_from_cache(self, movie_id: str) -> Optional[Movie]:
        """Получение данных о фильме из кэша по идентификатору"""
        data = await self.redis.get(movie_id)
        if not data:
            return None

        movie = Movie.parse_raw(data)
        return movie

    async def _put_movie_to_cache(self, movie: Movie):
        """Сохраняем данные о фильме, используя команду set"""
        await self.redis.set(
            str(movie.id), movie.json(), expire=FILM_CACHE_EXPIRE_IN_SECONDS
        )

    async def get_list(
        self,
        query: Optional[str] = None,
        page: Optional[dict] = None,
        filters: Optional[dict] = None,
        sort: Optional[dict] = None,
    ) -> List[Movie]:
        request_query = {}
        if query:
            request_query = {"multi_match": {"query": query, "fields": ["title"]}}
        elif filters:
            request_query.setdefault("match", {})
            for filter in filters:
                request_query["match"].setdefault(filter["field"], filter["value"])
        else:
            request_query = {"match_all": {}}

        request_sort = {}
        if sort:
            request_sort[sort["field"]] = sort["direction"]

        page_size = 50
        page_number = 1
        if page:
            page_size = page["size"]
            page_number = page["number"]

        response = await self.elastic.search(
            body={
                "query": request_query,
                "from": (page_number * page_size) - page_size,
                "size": page_size,
                "sort": request_sort,
            },
            index="movies",
        )

        return [Movie(**doc["_source"]) for doc in response["hits"]["hits"]]

    async def get_list_by_person_id(self, person_id: str) -> List[Movie]:
        response = await self.elastic.search(
            body={
                "query": {
                    "bool": {
                        "should": [
                            {
                                "nested": {
                                    "path": "actors",
                                    "query": {"match": {"actors.id": person_id}},
                                }
                            },
                            {
                                "nested": {
                                    "path": "directors",
                                    "query": {"match": {"directors.id": person_id}},
                                }
                            },
                            {
                                "nested": {
                                    "path": "writers",
                                    "query": {"match": {"writers.id": person_id}},
                                }
                            },
                        ]
                    },
                },
                "from": 0,
                "size": 1000,
            },
            index="movies",
        )

        return [Movie(**doc["_source"]) for doc in response["hits"]["hits"]]


@lru_cache()
def get_movie_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> MovieService:
    return MovieService(redis, elastic)
