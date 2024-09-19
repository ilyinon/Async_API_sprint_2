import http
import random

import pytest

from tests.functional.settings import settings
from tests.functional.testdata.genres import GENRES_DATA

pytestmark = pytest.mark.asyncio

async def test_genres_search(session, es_client, genres_index_create, genres_data_load):
    url_template = "{service_url}/api/v1/genres/"
    url = url_template.format(service_url=settings.app_dsn)
    async with session.get(url) as response:
        body = await response.json()
        assert response.status == http.HTTPStatus.OK
        assert len(body) == len(GENRES_DATA)


async def test_get_genre_by_id(
    session, es_client, genres_index_create, genres_data_load
):
    url_template = "{service_url}/api/v1/genres/{id}/"
    id = GENRES_DATA[random.randrange(len(GENRES_DATA))]["id"]
    url = url_template.format(service_url=settings.app_dsn, id=id)
    async with session.get(url) as response:
        assert response.status == http.HTTPStatus.OK


async def test_get_genre_by_not_existen_id(
    session,
    es_client,
    genres_index_create,
):
    url_template = "{service_url}/api/v1/genres/{id}/"
    id = "aaaaaaaa-1111-2222-3333-bbbbbbbbbbbb"
    url = url_template.format(service_url=settings.app_dsn, id=id)
    async with session.get(url) as response:
        assert response.status == http.HTTPStatus.NOT_FOUND
