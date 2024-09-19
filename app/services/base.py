import logging
from uuid import UUID

from core.config import settings
from elasticsearch import AsyncElasticsearch
from redis.asyncio import Redis

logger = logging.getLogger(__name__)


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
