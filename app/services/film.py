import hashlib
import logging
from functools import lru_cache
from uuid import UUID

from services.base import BaseService
from core.config import settings
from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from models.film import Film, FilmDetail
from redis.asyncio import Redis

logger = logging.getLogger(__name__)


class FilmService(BaseService):
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        super().__init__(redis, elastic)

    def _generate_cache_key(self, sort, genre, page_size, page_number):
        key_str = f"films:{sort}:{genre}:{page_size}:{page_number}"
        return hashlib.md5(key_str.encode()).hexdigest()

    async def get_by_id(self, film_id: UUID) -> FilmDetail | None:
        cache_key = self._generate_cache_key("id", film_id, "", "")
        film = await self.cache_service.get(cache_key, FilmDetail)
        
        if film is None:
            film = await self.search_service.get_by_id("movies", film_id)
            if film:
                await self.cache_service.set(cache_key, film, settings.film_cache_expire_in_seconds)
        
        return film

    async def get_list(self, sort, genre, page_size, page_number):
        cache_key = self._generate_cache_key(sort, genre, page_size, page_number)
        cached_data = await self.cache_service.get(cache_key, Film)

        if cached_data:
            return cached_data

        # Construct search query
        query = {"match_all": {}}
        sort_type = "asc" if sort[0] != "-" else "desc"

        if genre:
            genre_response = await self.search_service.search({"multi_match": {"query": genre}}, "genres")
            genre_names = " ".join([genre["_source"]["name"] for genre in genre_response])
            query = {"bool": {"must": [{"term": {"genres": genre_names}}]}} if genre_names else query

        offset = (page_number - 1) * page_size
        search_body = {
            "query": query,
            "sort": [{"imdb_rating": {"order": sort_type}}],
            "from": offset,
            "size": page_size,
        }

        films_list = await self.search_service.search(search_body, "movies")
        films = [Film(**get_film["_source"]) for get_film in films_list] if films_list else None
        
        if films:
            await self.cache_service.set(cache_key, films, settings.film_cache_expire_in_seconds)

        return films

    async def search_film(self, query, page_size, page_number):
        offset = (page_number - 1) * page_size
        search_body = {
            "query": {"multi_match": {"query": query}},
            "from": offset,
            "size": page_size,
        }
        films_list = await self.search_service.search(search_body, "movies")
        return [Film(**get_film["_source"]) for get_film in films_list] if films_list else None


@lru_cache()
def get_film_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
