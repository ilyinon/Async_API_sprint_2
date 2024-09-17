import hashlib
import logging
from functools import lru_cache
from uuid import UUID

from services.base import BaseService
from core.config import settings
from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from models.film import Film
from models.person import Person, PersonFilm
from redis.asyncio import Redis

logger = logging.getLogger(__name__)


class PersonService(BaseService):
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        super().__init__(redis, elastic)

    def _generate_cache_key(self, query, page_number, page_size):
        key_str = f"persons:{query}:{page_number}:{page_size}"
        return hashlib.md5(key_str.encode()).hexdigest()

    async def _get_person_films(self, person_id: UUID):
        film_list = await self.search_service.search(
            index=settings.movies_index,
            query={
                "bool": {
                    "should": [
                        {
                            "nested": {
                                "path": "directors",
                                "query": {"term": {"directors.id": person_id}},
                            },
                        },
                        {
                            "nested": {
                                "path": "actors",
                                "query": {"term": {"actors.id": person_id}},
                            },
                        },
                        {
                            "nested": {
                                "path": "writers",
                                "query": {"term": {"writers.id": person_id}},
                            }
                        },
                    ]
                }
            },
        )
        person_films = []
        for film in film_list:
            person_film = PersonFilm(id=film.get("id"), roles=[])
            if any(
                director["id"] == person_id for director in film.get("directors", [])
            ):
                person_film.roles.append("director")
            if any(actor["id"] == person_id for actor in film.get("actors", [])):
                person_film.roles.append("actor")
            if any(writer["id"] == person_id for writer in film.get("writers", [])):
                person_film.roles.append("writer")
            person_films.append(person_film)
        return person_films

    async def get_by_id(self, person_id: UUID) -> Person | None:
        cache_key = str(person_id)
        person = await self.cache_service.get(cache_key, Person)
        if person is None:
            person = await self.search_service.get_by_id("persons", person_id)
            if person:
                await self.cache_service.set(
                    cache_key, person, settings.person_cache_expire_in_seconds
                )
        return person

    async def get_person_film_list(self, person_id: UUID):
        search_body = {
            "bool": {
                "should": [
                    {
                        "nested": {
                            "path": "directors",
                            "query": {"term": {"directors.id": person_id}},
                        }
                    },
                    {
                        "nested": {
                            "path": "actors",
                            "query": {"term": {"actors.id": person_id}},
                        }
                    },
                    {
                        "nested": {
                            "path": "writers",
                            "query": {"term": {"writers.id": person_id}},
                        }
                    },
                ]
            }
        }
        try:
            film_list = await self.search_service.search(
                index=settings.movies_index,
                query={
                    "bool": {
                        "should": [
                            {
                                "nested": {
                                    "path": "directors",
                                    "query": {"term": {"directors.id": person_id}},
                                },
                            },
                            {
                                "nested": {
                                    "path": "actors",
                                    "query": {"term": {"actors.id": person_id}},
                                },
                            },
                            {
                                "nested": {
                                    "path": "writers",
                                    "query": {"term": {"writers.id": person_id}},
                                }
                            },
                        ]
                    }
                },
            )
        except NotFoundError:
            return None
        return [Film(**film) for film in film_list]

    async def get_search_list(self, query, page_number, page_size):
        cache_key = self._generate_cache_key(query, page_number, page_size)
        cached_data = await self.cache_service.get(cache_key, Person)

        if cached_data:
            return cached_data

        offset = (page_number - 1) * page_size
        try:
            persons_list = await self.search_service.search(
                index=settings.persons_index,
                from_=offset,
                size=page_size,
                query={"match": {"full_name": query}},
            )
        except NotFoundError:
            return None
        for get_person in persons_list["hits"]["hits"]:
            get_person["_source"]["films"] = await self._get_person_films(
                get_person["_source"]["id"]
            )
        persons = [
            Person(**get_person["_source"])
            for get_person in persons_list["hits"]["hits"]
        ]
        logger.debug(f"Search person {persons}")
        await self.cache_service.set(
            cache_key, persons, settings.person_cache_expire_in_seconds
        )

        return persons

    async def _get_object_from_elastic(self, person_id: UUID) -> Person | None:
        try:
            doc = await self.search_service.get_by_id("persons", person_id)
            person_data = {
                "id": doc.get("id"),
                "full_name": doc.get("full_name"),
                "films": await self._get_person_films(person_id),
            }
            logger.debug(f"Retrieved person {person_data} from elastic")
            return Person(**person_data)
        except NotFoundError:
            return None


@lru_cache()
def get_person_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
