import logging
from functools import lru_cache
from uuid import UUID

from services.base import BaseService
from core.config import settings
from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from models.genre import Genre
from redis.asyncio import Redis


logger = logging.getLogger(__name__)

class GenreService(BaseService):
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        super().__init__(redis, elastic)

    def _generate_cache_key(self, page_size, page_number):
        return f"genres_list:{page_size}:{page_number}"

    async def get_by_id(self, genre_id: UUID) -> Genre | None:
        cache_key = f"genre:{genre_id}"
        genre = await self.cache_service.get(cache_key, Genre)
        
        if genre is None:
            genre = await self.search_service.get_by_id("genres", genre_id)
            if genre:
                await self.cache_service.set(cache_key, genre, settings.genre_cache_expire_in_seconds)
        
        return genre

    async def get_list(self, page_number, page_size):
        cache_key = self._generate_cache_key(page_size, page_number)
        cached_data = await self.cache_service.get(cache_key, Genre)

        if cached_data:
            return cached_data

        offset = (page_number - 1) * page_size
        search_body = {
            "query": {"match_all": {}},
            "from": offset,
            "size": page_size,
        }

        genres_list = await self.search_service.search(search_body, "genres")
        genres = [Genre(**get_genre["_source"]) for get_genre in genres_list] if genres_list else None
        
        if genres:
            await self.cache_service.set(cache_key, genres, settings.genre_cache_expire_in_seconds)

        return genres


@lru_cache()
def get_genre_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic)
