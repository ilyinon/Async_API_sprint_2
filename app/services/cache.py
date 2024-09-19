import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Union
from uuid import UUID

from redis.asyncio import Redis

logger = logging.getLogger(__name__)


class AsyncCacheEngine(ABC):

    @abstractmethod
    def _generate_cache_key(self, *args: Union[str, int, UUID]) -> str:
        pass

    @abstractmethod
    async def get_from_cache(self, key: str, Object: Any) -> Any | None:
        pass

    @abstractmethod
    async def put_to_cache(self, key: str, object: Any, expiration: int) -> None:
        pass


class RedisCacheEngine(AsyncCacheEngine):
    def __init__(self, redis: Redis):
        self.redis = redis

    def _generate_cache_key(self, *args: Union[str, int, UUID]) -> str:
        """Generates a cache key based on multiple arguments for flexibility."""
        return ":".join(str(arg) for arg in args)

    async def get_from_cache(self, key: str, Object: Any) -> Any | None:
        cached_object = await self.redis.get(key)
        if not cached_object:
            return None
        logger.info(f"Retrieved {cached_object} from cache")
        return Object.parse_raw(cached_object)

    async def put_to_cache(self, key: str, object: Any, expiration: int) -> None:
        if isinstance(object, list):
            logger.info(f"Put list of {len(object)} items to cache with key {key}")
            serialized_object = json.dumps([item.json() for item in object])
        else:
            logger.info(f"Put {object} to cache with key {key}")
            serialized_object = object.json()

        await self.redis.set(key, serialized_object, expiration)


class BaseCache:
    def __init__(self, cache_engine: AsyncCacheEngine):
        self.cache_engine = cache_engine

    async def get_by_id(
        self, object_name: str, object_id: UUID, Object: Any
    ) -> Any | None:
        """Retrieve object by its name and ID from cache."""
        key = self.cache_engine._generate_cache_key(object_name, object_id)
        return await self.cache_engine.get_from_cache(key, Object)

    async def put_by_id(self, object_name: str, object: Any, expiration: int) -> None:
        """Store object by its name and ID in cache."""
        key = self.cache_engine._generate_cache_key(object_name, object.id)
        await self.cache_engine.put_to_cache(key, object, expiration)

    async def get_by_key(self, *args: Union[str, int], Object: Any) -> Any | None:
        """Retrieve object from cache using a flexible key."""
        key = self.cache_engine._generate_cache_key(*args)
        return await self.cache_engine.get_from_cache(key, Object)

    async def put_by_key(self, object: Any, expiration: int, *args: Union[str, int]) -> None:
        """Store object in cache using a flexible key."""
        key = self.cache_engine._generate_cache_key(*args)
        await self.cache_engine.put_to_cache(key, object, expiration)
