import logging
import json
from core.config import settings
from redis.asyncio import Redis

logger = logging.getLogger(__name__)

class CacheService:
    async def get(self, key: str):
        raise NotImplementedError()

    async def set(self, key: str, value: str, expiry_time: int):
        raise NotImplementedError()


class RedisCacheService(CacheService):
    def __init__(self, redis: Redis):
        self.redis = redis

    async def get(self, key: str):
        value = await self.redis.get(key)
        if value:
            logger.info(f"Cache hit for key: {key}")
            return json.loads(value)
        logger.info(f"Cache miss for key: {key}")
        return None

    async def set(self, key: str, value: str, expire_time: int):
        logger.info(f"Setting cache for key: {key}")
        await self.redis.set(key, json.dumps(value), expire_time)
