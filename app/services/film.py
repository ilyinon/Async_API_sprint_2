import json
import logging
from functools import lru_cache
from uuid import UUID, uuid4

from core.config import settings
from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from models.film import Film, FilmDetail
from redis.asyncio import Redis
from services.cache import BaseCache, RedisCacheEngine
from services.search import BaseSearch, ElasticAsyncSearchEngine

logger = logging.getLogger(__name__)


class FilmService:
    def __init__(self, cache_engine: BaseCache, search_engine: BaseSearch):
        self.search_engine = search_engine
        self.cache_engine = cache_engine

    async def get_by_id(self, film_id: UUID) -> FilmDetail | None:

        film = await self.cache_engine.get_by_id("film", film_id, FilmDetail)
        try:
            film_data = await self.search_engine.get_by_id(
                settings.movies_index, film_id
            )

            if not film_data:
                return None

        except NotFoundError:
            return None

        except Exception as e:
            logger.error(f"Error retrieving film by id {film_id}: {e}")
            return None

        if "genres" in film_data:
            film_data["genres"] = [
                (
                    {"id": genre["id"], "name": genre["name"]}
                    if isinstance(genre, dict)
                    else {"id": str(uuid4()), "name": genre}
                )
                for genre in film_data["genres"]
            ]

        if "actors" in film_data:
            film_data["actors"] = [
                {"id": actor.get("id", None), "full_name": actor.get("name", "")}
                for actor in film_data["actors"]
            ]

        if "writers" in film_data:
            film_data["writers"] = [
                {"id": writer.get("id", None), "full_name": writer.get("name", "")}
                for writer in film_data["writers"]
            ]

        if "directors" in film_data:
            film_data["directors"] = [
                {"id": director.get("id", None), "full_name": director.get("name", "")}
                for director in film_data["directors"]
            ]

        film = FilmDetail(**film_data)

        await self.cache_engine.put_by_id(
            "film", film, settings.film_cache_expire_in_seconds
        )

        logger.info(f"Retrieved film: {film}")
        return film

    async def get_list(self, sort, genre, page_size, page_number):
        cache_key_args = ("films_list", page_size, page_number)
        cached_data = await self.cache_engine.get_by_key(*cache_key_args, Object=Film)

        if cached_data:
            return [Film.parse_raw(film) for film in json.loads(cached_data)]

        query = {"match_all": {}}
        logger.debug(
            f"Search type {sort}",
        )
        sort_type = "asc"
        if sort and sort[0].startswith("-"):
            sort_type = "desc"

        if genre:
            genre_response = await self.search_engine.search(
                index=settings.genres_index, query={"multi_match": {"query": genre}}
            )
            genre_names = " ".join(
                [genre["_source"]["name"] for genre in genre_response["hits"]["hits"]]
            )

            logger.debug(f"Genre list {genre_names}")

            if genre_names:
                query = {"bool": {"must": [{"term": {"genres": genre_names}}]}}

        offset = (page_number - 1) * page_size

        try:
            films_list = await self.search_engine.search(
                index=settings.movies_index,
                query={"bool": {"must": [query]}},
                sort=[{"imdb_rating": {"order": sort_type}}],
                from_=offset,
                size=page_size,
            )

            logger.debug(f"Retrieved films {films_list}")
        except NotFoundError:
            return None

        if isinstance(films_list, dict):
            films = [
                Film(**get_film["_source"]) for get_film in films_list["hits"]["hits"]
            ]
        else:
            films = [Film(**get_film) for get_film in films_list]

        await self.cache_engine.put_by_key(
            json.dumps([film.json() for film in films]),
            settings.film_cache_expire_in_seconds,
            *cache_key_args,
        )

        return films

    async def search_film(self, query, page_size, page_number):
        offset = (page_number - 1) * page_size
        try:
            films_list = await self.search_engine.search(
                index=settings.movies_index,
                from_=offset,
                size=page_size,
                query={"multi_match": {"query": query}},
            )
        except NotFoundError:
            return None
        except Exception as e:
            logger.error(f"Error searching for films with query '{query}': {e}")
            return None

        logger.debug(f"Searched films {films_list}")
        return [Film(**get_film["_source"]) for get_film in films_list["hits"]["hits"]]


@lru_cache()
def get_film_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:

    redis_cache_engine = RedisCacheEngine(redis)
    cache_engine = BaseCache(redis_cache_engine)

    elastic_search_engine = ElasticAsyncSearchEngine(elastic)
    search_engine = BaseSearch(search_engine=elastic_search_engine)

    return FilmService(cache_engine, search_engine)
