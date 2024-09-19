import http
import random

import pytest

from tests.functional.settings import settings
from tests.functional.testdata.persons import PERSONS_DATA

pytestmark = pytest.mark.asyncio

async def test_persons_search(
    session, es_client, persons_index_create, persons_data_load, movies_index_create, movies_data_load
):
    url_template = (
        "{service_url}/api/v1/persons/search?page_size=50&page_number=1&query=James"
    )
    url = url_template.format(service_url=settings.app_dsn)
    async with session.get(url) as response:

        body = await response.json()

        assert response.status == http.HTTPStatus.OK
        assert body[0]["uuid"] == "807ce9c3-6294-485c-803a-1975066f239f"


async def test_get_person_by_id(
    session, es_client, persons_index_create, persons_data_load, movies_index_create, movies_data_load
):
    url_template = "{service_url}/api/v1/persons/{id}/"
    id = PERSONS_DATA[random.randrange(len(PERSONS_DATA))]["id"]
    url = url_template.format(service_url=settings.app_dsn, id=id)
    async with session.get(url) as response:

        assert response.status == http.HTTPStatus.OK


async def test_get_person_films_by_id(
    session, es_client, persons_index_create, persons_data_load, movies_index_create, movies_data_load
):
    url_template = "{service_url}/api/v1/persons/{id}/film"
    id = PERSONS_DATA[random.randrange(len(PERSONS_DATA))]["id"]
    url = url_template.format(service_url=settings.app_dsn, id=id)
    async with session.get(url) as response:

        assert response.status == http.HTTPStatus.OK


async def test_get_persons_by_not_existen_id(
    session,
    es_client,
    persons_index_create,
):
    url_template = "{service_url}/api/v1/persons/{id}/"
    id = "aaaaaaaa-1111-2222-3333-bbbbbbbbbbbb"
    url = url_template.format(service_url=settings.app_dsn, id=id)
    async with session.get(url) as response:

        assert response.status == http.HTTPStatus.NOT_FOUND


async def test_get_persons_with_id_invalid(
        session, es_client, persons_index_create,
):
    url_template = "{service_url}/api/v1/persons/{id}/"
    id = "not_valid_uuid"
    url = url_template.format(service_url=settings.app_dsn, id=id)
    async with session.get(url) as response:

        assert response.status == http.HTTPStatus.UNPROCESSABLE_ENTITY


async def test_persons_search_invalid(
    session, es_client, persons_index_create, persons_data_load, movies_index_create, movies_data_load
):
    url_template = (
        "{service_url}/api/v1/persons/search?this_search_not_existen"
    )
    url = url_template.format(service_url=settings.app_dsn)
    async with session.get(url) as response:

        body = await response.json()
        
        assert response.status == http.HTTPStatus.OK
        assert body == []