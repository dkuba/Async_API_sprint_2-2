from functools import lru_cache
from typing import Optional

import elasticsearch.exceptions
from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from models.movie import Genre


class GenreService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, genre_id: str) -> Optional[Genre]:
        try:
            doc = await self.elastic.get("genres", genre_id)
        except elasticsearch.exceptions.NotFoundError:
            return None

        return Genre(**doc["_source"])

    async def get_list(self, page: Optional[dict] = None) -> list[Genre]:
        page_size = 50
        page_number = 1
        if page:
            page_size = page["size"]
            page_number = page["number"]

        response = await self.elastic.search(
            body={
                "query": {"match_all": {}},
                "from": (page_number * page_size) - page_size,
                "size": page_size,
            },
            index="genres",
        )

        return [Genre(**doc["_source"]) for doc in response["hits"]["hits"]]


@lru_cache()
def get_genre_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic)
