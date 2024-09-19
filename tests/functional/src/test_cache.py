import hashlib
import json
import pytest
import random

from tests.functional.settings import settings
from tests.functional.testdata.genres import GENRES_DATA
from tests.functional.testdata.persons import PERSONS_DATA

from tests.functional.utils.logger import logger

pytestmark = pytest.mark.asyncio


async def test_genres_search_cache(session, es_client, redis_client, genres_index_create, genres_data_load):
    url_template = "{service_url}/api/v1/genres/"
    url = url_template.format(service_url=settings.app_dsn)
    cache_key = "genres_list:50:1"

    async with session.get(url) as response:

        cached_data = await redis_client.get(cache_key)
        assert len(json.loads(cached_data)) == len(GENRES_DATA)


async def test_get_person_by_id_cache(
    session, redis_client, es_client, movies_index_create, movies_data_load, persons_index_create, persons_data_load
):
    url_template = "{service_url}/api/v1/persons/{id}/"
    id = PERSONS_DATA[random.randrange(len(PERSONS_DATA))]["id"]
    url = url_template.format(service_url=settings.app_dsn, id=id)

    async with session.get(url) as response:

        cached_data = await redis_client.get(f"person:{str(id)}")

        assert json.loads(cached_data).get("id") == id


async def test_movies_search_sort_asc_cache(
    session, redis_client, es_client, movies_index_create, movies_data_load
):
    url_template = "{service_url}/api/v1/films/?sort=imdb_rating"
    url = url_template.format(service_url=settings.app_dsn)
    cache_key = "films_list:50:1:['imdb_rating']"

    async with session.get(url) as response:

        cached_data = await redis_client.get(cache_key)

        assert json.loads(cached_data)[0][7:43] == "7429fb65-1436-4035-832d-3ef8fb8851fa"


