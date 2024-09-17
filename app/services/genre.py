import json
import logging
from functools import lru_cache
from uuid import UUID

from core.config import settings
from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from models.genre import Genre
from redis.asyncio import Redis
from services.base import BaseServiceElastic, BaseServiceRedis

logger = logging.getLogger(__name__)


class GenreService(BaseServiceRedis, BaseServiceElastic):
    async def get_by_id(self, film_id):
        return await self._get_by_id(film_id, Genre)

    async def get_list(self, page_number, page_size):
        cache_key = f"genres_list:{page_size}:{page_number}"
        cached_data = await self.redis.get(cache_key)
        offset = (page_number - 1) * page_size
        if cached_data:
            return [Genre.parse_raw(genre) for genre in json.loads(cached_data)]

        try:
            genres_list = await self.elastic.search(
                index=settings.genres_index,
                from_=offset,
                size=page_size,
                query={"match_all": {}},
            )
        except NotFoundError:
            return None

        genres = [
            Genre(**get_genre["_source"]) for get_genre in genres_list["hits"]["hits"]
        ]
        await self.redis.set(
            cache_key,
            json.dumps([genre.json() for genre in genres]),
            settings.genre_cache_expire_in_seconds,
        )

        return genres

    async def _get_object_from_elastic(self, genre_id: UUID) -> Genre | None:
        try:
            doc = await self.elastic.get(index=settings.genres_index, id=genre_id)
        except NotFoundError:
            return None
        answer = {}
        answer["id"] = doc["_source"]["id"]
        answer["name"] = doc["_source"]["name"]
        return Genre(**answer)


@lru_cache()
def get_genre_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic)
