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

logger = logging.getLogger(__name__)


class PersonService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    def _generate_cache_key(self, query, page_number, page_size):
        key_str = f"persons:{query}:{page_number}:{page_size}"
        return hashlib.md5(key_str.encode()).hexdigest()

    async def get_person_films(self, person_id: UUID):
        film_list = await self.elastic.search(
            index="movies",
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
        person = await self._person_from_cache(person_id)
        if not person:
            person = await self._get_person_from_elastic(person_id)
            if not person:
                return None
            await self._put_person_to_cache(person)
        return person

    async def get_list(self):
        cache_key = "persons_list"
        cached_data = await self.redis.get(cache_key)
        if cached_data:
            return [Person.parse_raw(person) for person in json.loads(cached_data)]

        try:
            persons_list = await self.elastic.search(
                index="persons", query={"match_all": {}}
            )
        except NotFoundError:
            return None

        persons = [
            Person(**get_person["_source"])
            for get_person in persons_list["hits"]["hits"]
        ]
        await self.redis.set(
            cache_key,
            json.dumps([person.json() for person in persons]),
            settings.person_cache_expire_in_seconds,
        )

        return persons

    async def get_person_film_list(self, person_id):
        try:
            film_list = await self.elastic.search(
                index="movies",
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
        return [Film(**film["_source"]) for film in film_list["hits"]["hits"]]

    async def get_search_list(self, query, page_number, page_size):
        cache_key = self._generate_cache_key(query, page_number, page_size)
        cached_data = await self.redis.get(cache_key)
        if cached_data:
            return [Person.parse_raw(person) for person in json.loads(cached_data)]

        offset = (page_number - 1) * page_size
        try:
            persons_list = await self.elastic.search(
                index="persons",
                from_=offset,
                size=page_size,
                query={"match": {"full_name": query}},
            )
        except NotFoundError:
            return None
        for get_person in persons_list["hits"]["hits"]:
            get_person["_source"]["films"] = await self.get_person_films(
                get_person["_source"]["id"]
            )
        persons = [
            Person(**get_person["_source"])
            for get_person in persons_list["hits"]["hits"]
        ]
        logger.debug(f"Search person {persons}")
        await self.redis.set(
            cache_key,
            json.dumps([person.json() for person in persons]),
            settings.person_cache_expire_in_seconds,
        )

        return persons

    async def _get_person_from_elastic(self, person_id: UUID) -> Person | None:
        try:
            doc = await self.elastic.get(index="persons", id=person_id)
        except NotFoundError:
            return None
        answer = {}
        answer["id"] = doc["_source"]["id"]
        answer["full_name"] = doc["_source"]["full_name"]

        films = await self.get_person_films(answer["id"])
        answer["films"] = films
        logger.debug(f"Retrieved person {answer} from elastic")
        return Person(**answer)

    async def _person_from_cache(self, person_id: UUID) -> Person | None:
        data = await self.redis.get(str(person_id))
        if not data:
            return None
        logger.debug(f"Retrieved person {person_id} from cache")
        person = Person.parse_raw(data)
        return person

    async def _put_person_to_cache(self, person: Person):
        await self.redis.set(
            str(person.id), person.json(), settings.person_cache_expire_in_seconds
        )


@lru_cache()
def get_person_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
