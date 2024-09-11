import hashlib
import json
import logging
from functools import lru_cache
from uuid import UUID

from core.config import settings
from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from models.film import Film, FilmDetail
from redis.asyncio import Redis

logger = logging.getLogger(__name__)


class FilmService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, film_id: UUID) -> FilmDetail | None:
        film = await self._film_from_cache(film_id)
        if not film:
            film = await self._get_film_from_elastic(film_id)
            if not film:
                return None
            await self._put_film_to_cache(film)

        return film

    def _generate_cache_key(self, sort, genre, page_size, page_number):
        key_str = f"films:{sort}:{genre}:{page_size}:{page_number}"
        return hashlib.md5(key_str.encode()).hexdigest()

    async def get_list(self, sort, genre, page_size, page_number):
        cache_key = self._generate_cache_key(sort, genre, page_size, page_number)

        cached_data = await self.redis.get(cache_key)
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
            genre_response = await self.elastic.search(
                index="genres", query={"multi_match": {"query": genre}}
            )
            genre_names = " ".join(
                [genre["_source"]["name"] for genre in genre_response["hits"]["hits"]]
            )

            logger.debug(f"Genre list {genre_names}")

            if genre_names:
                query = {"bool": {"must": [{"term": {"genres": genre_names}}]}}

        offset = (page_number - 1) * page_size

        try:
            films_list = await self.elastic.search(
                index="movies",
                body={
                    "query": query,
                    "sort": [{"imdb_rating": {"order": sort_type}}],
                    "from": offset,
                    "size": page_size,
                },
            )
            logger.debug(f"Retrieved films {films_list}")
        except NotFoundError:
            return None

        films = [Film(**get_film["_source"]) for get_film in films_list["hits"]["hits"]]
        await self.redis.set(
            cache_key,
            json.dumps([film.json() for film in films]),
            settings.film_cache_expire_in_seconds,
        )

        return films

    async def search_film(self, query, page_size, page_number):
        offset = (page_number - 1) * page_size
        try:
            films_list = await self.elastic.search(
                index="movies",
                from_=offset,
                size=page_size,
                query={"multi_match": {"query": query}},
            )
        except NotFoundError:
            return None
        logger.debug(f"Searched films {films_list}")
        return [Film(**get_film["_source"]) for get_film in films_list["hits"]["hits"]]

    async def _get_film_from_elastic(self, film_id: UUID) -> FilmDetail | None:
        try:
            doc = await self.elastic.get(index="movies", id=film_id)
            genres = doc["_source"].get("genres", [])
            logger.debug(f"genres list: {genres}")
            genres_list = []
            for genre in genres:
                response = await self.elastic.search(
                    index="genres", query={"multi_match": {"query": genre}}
                )

                genres_list.append(response["hits"]["hits"][0]["_source"])
            actors = doc["_source"].get("actors", [])
            if isinstance(actors, str):
                actors = []

            writers = doc["_source"].get("writers", [])
            if isinstance(writers, str):
                writers = []

            directors = doc["_source"].get("directors", [])
            if isinstance(directors, str):
                directors = []
        except NotFoundError:
            logger.error(f"Film with ID {film_id} not found in Elasticsearch")
            return None

        film_data = {
            "id": doc["_source"].get("id"),
            "title": doc["_source"].get("title"),
            "imdb_rating": doc["_source"].get("imdb_rating"),
            "description": doc["_source"].get("description", ""),
            "genres": genres_list,
            "actors": [
                {"id": actor.get("id"), "full_name": actor.get("name")}
                for actor in actors
                if isinstance(actor, dict)
            ],
            "writers": [
                {"id": writer.get("id"), "full_name": writer.get("name")}
                for writer in writers
                if isinstance(writer, dict)
            ],
            "directors": [
                {"id": director.get("id"), "full_name": director.get("name")}
                for director in directors
                if isinstance(director, dict)
            ],
        }
        logger.debug("Got film details {film_data}")
        return FilmDetail(**film_data)

    async def _film_from_cache(self, film_id: UUID) -> Film | None:
        data = await self.redis.get(str(film_id))
        if not data:
            return None
        logger.debug(f"Retrieved film {film_id} from cache")
        film = Film.parse_raw(data)
        return film

    async def _put_film_to_cache(self, film: Film):
        await self.redis.set(
            str(film.id), film.json(), settings.film_cache_expire_in_seconds
        )


@lru_cache()
def get_film_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
