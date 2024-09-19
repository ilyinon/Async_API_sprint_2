import json
import logging
from functools import lru_cache
from uuid import UUID

from core.config import settings
from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from models.genre import Genre
from redis.asyncio import Redis
from services.cache import BaseCache, RedisCacheEngine
from services.search import BaseSearch, ElasticAsyncSearchEngine

logger = logging.getLogger(__name__)


class GenreService:
    def __init__(self, cache_engine: BaseCache, search_engine: BaseSearch):
        self.search_engine = search_engine
        self.cache_engine = cache_engine

    async def get_by_id(self, genre_id: UUID) -> Genre | None:
        genre = await self.cache_engine.get_by_id('genre', genre_id, Genre)

        if not genre:
            genre_data = await self.search_engine.get_by_id(
                settings.genres_index, genre_id
            )

            if not genre_data:
                return None

            genre = Genre(**genre_data)

            await self.cache_engine.put_by_id('genre', genre, settings.genre_cache_expire_in_seconds)

        logger.info(f"Retrieved genre: {genre}")
        return genre

    async def get_list(self, page_number: int, page_size: int) -> list[Genre] | None:
        cache_key_args = ("genres_list", page_size, page_number)
        cached_data = await self.cache_engine.get_by_key(*cache_key_args, Object=Genre)

        if cached_data:
            return [Genre.parse_raw(genre) for genre in json.loads(cached_data)]

        offset = (page_number - 1) * page_size

        genres_list = await self.search_engine.search(
            index=settings.genres_index,
            query={"match_all": {}},
            from_=offset,
            size=page_size,
        )

        if not genres_list:
            return None

        genres = [Genre(**genre) for genre in genres_list]

        await self.cache_engine.put_by_key(genres, settings.genre_cache_expire_in_seconds, *cache_key_args)

        return genres


@lru_cache()
def get_genre_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:

    redis_cache_engine = RedisCacheEngine(redis)
    cache_engine = BaseCache(redis_cache_engine)

    elastic_search_engine = ElasticAsyncSearchEngine(elastic)
    search_engine = BaseSearch(search_engine=elastic_search_engine)

    return GenreService(cache_engine, search_engine)
