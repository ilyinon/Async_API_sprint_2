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
from models.film import Film
from models.person import Person, PersonFilm
from redis.asyncio import Redis
from services.cache import BaseCache, RedisCacheEngine
from services.search import BaseSearch, ElasticAsyncSearchEngine

logger = logging.getLogger(__name__)


class PersonService:
    def __init__(self, cache_engine: BaseCache, search_engine: BaseSearch):
        self.search_engine = search_engine
        self.cache_engine = cache_engine

    async def _get_person_films(self, person_id: UUID):
        film_list = await self.search_engine.search(
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

        # Check if film_list is a dict and has 'hits'
        if isinstance(film_list, dict) and "hits" in film_list:
            film_hits = film_list["hits"]["hits"]
        elif isinstance(film_list, list):
            film_hits = film_list  # Directly use if it's a list
        else:
            return []  # Return empty if the structure is unexpected

        person_films = []
        for film in film_hits:
            # Safely access '_source' with a fallback to an empty dict
            source = film.get("_source", {})
            
            # Ensure 'id' and roles lists are present
            film_id = source.get("id")
            if film_id is None:
                continue  # Skip if no film ID

            person_film = PersonFilm(id=film_id, roles=[])

            # Process roles with default to empty list
            for role_type in ['directors', 'actors', 'writers']:
                for person in source.get(role_type, []):
                    if person["id"] == person_id and role_type[:-1] not in person_film.roles:
                        person_film.roles.append(role_type[:-1])  # Add role without 's'

            person_films.append(person_film)

        return person_films

    async def get_by_id(self, person_id: UUID) -> Person | None:
        person = await self.cache_engine.get_by_id("person", person_id, Person)

        if not person:
            person_data = await self.search_engine.get_by_id(
                settings.persons_index, person_id
            )

            if not person_data:
                return None

            films = await self._get_person_films(person_id)

            person_data["films"] = (
                [PersonFilm(**film) for film in films] if films else []
            )

            person = Person(**person_data)

            await self.cache_engine.put_by_id(
                "person", person, settings.person_cache_expire_in_seconds
            )

        logger.info(f"Retrieved person: {person}")
        return person

    async def get_person_film_list(self, person_id):
        try:
            film_list = await self.search_engine.search(
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

        if (
            isinstance(film_list, dict)
            and "hits" in film_list
            and "hits" in film_list["hits"]
        ):
            return [Film(**film["_source"]) for film in film_list["hits"]["hits"]]
        elif isinstance(film_list, list):
            return [Film(**film) for film in film_list]

        return []

    async def get_search_list(self, query, page_number, page_size):
        cache_key_args = ("persons_list", page_size, page_number)
        cached_data = await self.cache_engine.get_by_key(*cache_key_args, Object=Person)

        if cached_data:
            return [Person.parse_raw(person) for person in json.loads(cached_data)]

        offset = (page_number - 1) * page_size
        try:
            persons_list = await self.search_engine.search(
                index=settings.persons_index,
                from_=offset,
                size=page_size,
                query={"match": {"full_name": query}},
            )
        except NotFoundError:
            logger.error(f"Persons not found for query: {query}")
            return []

        logger.debug(f"Persons list response: {persons_list}")

        if isinstance(persons_list, dict) and "hits" in persons_list:
            if "hits" in persons_list and isinstance(
                persons_list["hits"]["hits"], list
            ):
                for get_person in persons_list["hits"]["hits"]:
                    get_person["_source"]["films"] = await self._get_person_films(
                        get_person["_source"]["id"]
                    )
                persons = [
                    Person(**get_person["_source"])
                    for get_person in persons_list["hits"]["hits"]
                ]
                await self.cache_engine.put_by_key(
                    json.dumps([person.json() for person in persons]),
                    settings.person_cache_expire_in_seconds,
                    *cache_key_args,
                )
                return persons
            else:
                logger.error("Unexpected format for 'hits': expected a list.")
                return []
        elif isinstance(persons_list, list):
            persons = [
                Person(
                    id=person["id"],
                    full_name=person["full_name"],
                    films=person.get("films", []),
                )
                for person in persons_list
            ]
            return persons

        return []


@lru_cache()
def get_person_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:

    redis_cache_engine = RedisCacheEngine(redis)
    cache_engine = BaseCache(redis_cache_engine)

    elastic_search_engine = ElasticAsyncSearchEngine(elastic)
    search_engine = BaseSearch(search_engine=elastic_search_engine)

    return PersonService(cache_engine, search_engine)
