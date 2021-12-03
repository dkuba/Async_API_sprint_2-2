"""Начальная точка входа для всего приложения"""
import aioredis
import uvicorn
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api.v1.routes import api_v1_router
from api_cache.backends.redis import RedisBackend
from api_cache.cache import APICache
from core import config
from db import elastic, redis

app = FastAPI(
    title=config.PROJECT_NAME,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)


@app.on_event("startup")
async def startup():
    redis.redis = await aioredis.create_redis_pool(
        (config.REDIS_HOST, config.REDIS_PORT), minsize=10, maxsize=20, encoding="utf8"
    )
    elastic.es = AsyncElasticsearch(
        hosts=[f"{config.ELASTIC_HOST}:{config.ELASTIC_PORT}"]
    )

    redis_storage = await redis.get_redis()
    APICache.init(RedisBackend(redis_storage), prefix="movies-async-api")


@app.on_event("shutdown")
async def shutdown():
    await redis.redis.close()
    await elastic.es.close()


app.include_router(api_v1_router, prefix="/api/v1")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
    )
