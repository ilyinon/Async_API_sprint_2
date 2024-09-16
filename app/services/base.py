import logging
from elasticsearch import AsyncElasticsearch
from redis.asyncio import Redis

from services.cache import RedisCacheService
from services.search import ElasticSearchService

logger = logging.getLogger(__name__)

class BaseService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.cache_service = RedisCacheService(redis)
        self.search_service = ElasticSearchService(elastic)

