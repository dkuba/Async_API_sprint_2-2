from aioredis import Redis

from api_cache.backends._abstract import Backend


class RedisBackend(Backend):
    def __init__(self, redis: Redis):
        self.redis = redis

    async def get(self, key) -> str:
        return await self.redis.get(key)

    async def set(self, key: str, value: str, expire: int = None):
        return await self.redis.set(key, value, expire=expire)
