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
        person_films = []
        for film in film_list["hits"]["hits"]:
            person_film = PersonFilm(id=film.get("_source").get("id"), roles=[])
            for director in film.get("_source").get("directors"):
                if director["id"] == person_id and "director" not in person_film.roles:
                    person_film.roles.append("director")
            for actor in film.get("_source").get("actors"):
                if actor["id"] == person_id and "actor" not in person_film.roles:
                    person_film.roles.append("actor")
            for writer in film.get("_source").get("writers"):
                if writer["id"] == person_id and "writer" not in person_film.roles:
                    person_film.roles.append("writer")
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
            
            person_data.setdefault("films", [])

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
            persons = [Person(**person) for person in persons_list]
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
