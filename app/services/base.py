from abc import ABC, abstractmethod
import logging
from typing import Any
from uuid import UUID

from core.config import settings
from elasticsearch import AsyncElasticsearch
from redis.asyncio import Redis

logger = logging.getLogger(__name__)

class AsyncSearchEngine(ABC):
    @abstractmethod
    async def get_by_id(self, index: str, _id: str) -> Any | None:
        pass

    @abstractmethod
    async def _get_by_ids(self, index: str, ids: list[str]) -> list[Any] | None:
        pass

    @abstractmethod
    async def search(self, index: str, query: dict) -> list[Any]:
        pass


class ElasticAsyncSearchEngine(AsyncSearchEngine):
    def __init__(self, client: AsyncElasticsearch):
        self.client = client

    async def get_by_id(self, index: str, _id: str) -> Any | None:
        try:
            result = await self.client.get(index=index, id=_id)
            return result["_source"]
        except Exception:
            return None

    async def get_by_ids(self, index: str, ids: list[str]) -> list[Any] | None:
        try:
            result = await self.client.mget(index=index, body={"ids": ids})
            return [doc["_source"] for doc in result["docs"] if doc["found"]]
        except Exception:
            return []

    async def search(self, index: str, query: dict) -> list[Any]:
        try:
            result = await self.client.search(index=index, body=query)
            return [hit["_source"] for hit in result["hits"]["hits"]]
        except Exception:
            return []

class BaseService234(ABC):
    def __init__(self, search_engine: AsyncSearchEngine):
        self.search_engine = search_engine

    async def get_by_id(self, index: str, obj_id: str) -> Any | None:
        obj = await self.search_engine.get_by_id(index=index, _id=obj_id)
        return obj

    async def get_by_ids(self, index: str, obj_ids: list[str]) -> list[Any]:
        objs = await self.search_engine.get_by_ids(index=index, ids=obj_ids)
        return objs

    async def search(self, index: str, query: dict) -> list[Any]:
        objs = await self.search_engine.search(index=index, query=query)
        return objs



# class BaseService(abc.ABC):
#     def __init__(self, search_engine: AsyncSearchEngine):
#         self.search_engine = search_engine

#     async def get_by_id(self, obj_id: str) -> Optional[BaseServiceModelChild]:
#         obj = await self.search_engine.get_by_id(obj_id)
#         return obj


class BaseService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic


class BaseServiceRedis(BaseService):
    def _generate_cache_key_by_id(self, object_name, object_id):
        return f"{object_name}:{object_id}"

    async def _get_object_from_cache(self, object_id: UUID, Object):
        object = await self.redis.get(str(object_id))
        if not object:
            return None
        logger.info(f"Retrieved {object} from cache")
        return Object.parse_raw(object)

    async def _put_object_to_cache(self, object):
        logger.info(f"Put to cache {object}")

        await self.redis.set(
            str(object.id), object.json(), settings.film_cache_expire_in_seconds
        )


class BaseServiceElastic(BaseService):
    async def _get_by_id(self, object_id: UUID, Object):
        logger.info(f"the object_id is {object_id}")
        object = await self._get_object_from_cache(object_id, Object)
        if not object:
            object = await self._get_object_from_elastic(object_id)
            if not object:
                return None
            await self._put_object_to_cache(object)
        logger.info(f"The object is {object}")
        return object
