from functools import lru_cache
from typing import Optional

import elasticsearch.exceptions
from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from models.person import Person


class PersonService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, person_id: str) -> Optional[Person]:
        try:
            doc = await self.elastic.get("persons", person_id)
        except elasticsearch.exceptions.NotFoundError:
            return None

        return Person(**doc["_source"])

    async def get_list(
        self,
        query: Optional[str] = None,
        page: Optional[dict] = None,
    ) -> list[Person]:
        request_query = {}
        if query:
            request_query = {"multi_match": {"query": query, "fields": ["full_name"]}}
        else:
            request_query = {"match_all": {}}

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
            },
            index="persons",
        )

        return [Person(**doc["_source"]) for doc in response["hits"]["hits"]]


@lru_cache()
def get_person_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
