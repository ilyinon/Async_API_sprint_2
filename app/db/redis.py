from fastapi import Depends
from redis.asyncio import Redis
from core.config import settings

# Initialize Redis connection
async def init_redis() -> Redis:
    redis = Redis.from_url(settings.redis_dsn)
    return redis

# Dependency for getting Redis connection
async def get_redis(redis: Redis = Depends(init_redis)) -> Redis:
    return redis
