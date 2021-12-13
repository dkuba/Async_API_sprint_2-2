from functools import lru_cache
from typing import List, Optional

import elasticsearch.exceptions
from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from models.movie import Movie


class MovieService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, movie_id: str) -> Optional[Movie]:
        """Возвращает объект фильма. Он опционален, так как фильм может
        отсутствовать в базе.
        """
        try:
            doc = await self.elastic.get("movies", movie_id)
        except elasticsearch.exceptions.NotFoundError:
            return None

        return Movie(**doc["_source"])

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
            request_filters = []
            for filter in filters:
                request_filters.append({"term": {filter["field"]: filter["value"]}})

            request_query = {
                "nested": {
                    "path": "genres",
                    "query": {"bool": {"must": request_filters}},
                }
            }
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
