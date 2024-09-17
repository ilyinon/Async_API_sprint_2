import http
import random

import pytest

from tests.functional.settings import settings
from tests.functional.testdata.movies import MOVIES_DATA


@pytest.mark.asyncio
async def test_movies_search(session, es_client, movies_index_create, movies_data_load):
    url_template = "{service_url}/api/v1/films/"
    url = url_template.format(service_url=settings.app_dsn)
    async with session.get(url) as response:
        body = await response.json()
        assert response.status == http.HTTPStatus.OK
        assert len(body) == 50


@pytest.mark.asyncio
async def test_get_movie_by_id(
    session,
    es_client,
    movies_index_create,
    movies_data_load,
    genres_index_create,
    genres_data_load,
):
    url_template = "{service_url}/api/v1/films/{id}/"
    id = MOVIES_DATA[random.randrange(len(MOVIES_DATA))]["id"]
    url = url_template.format(service_url=settings.app_dsn, id=id)
    async with session.get(url) as response:
        assert response.status == http.HTTPStatus.OK


@pytest.mark.asyncio
async def test_movies_search_sort_asc(
    session, es_client, movies_index_create, movies_data_load
):
    url_template = "{service_url}/api/v1/films/?sort=imdb_rating"
    url = url_template.format(service_url=settings.app_dsn)
    async with session.get(url) as response:
        body = await response.json()
        assert response.status == http.HTTPStatus.OK
        assert body[0]["uuid"] == "7429fb65-1436-4035-832d-3ef8fb8851fa"


@pytest.mark.asyncio
async def test_movies_search_sort_desc(
    session, es_client, movies_index_create, movies_data_load
):
    url_template = "{service_url}/api/v1/films/?sort=-imdb_rating"
    url = url_template.format(service_url=settings.app_dsn)
    async with session.get(url) as response:
        body = await response.json()
        assert response.status == http.HTTPStatus.OK
        assert body[0]["uuid"] == "562ca232-b898-4d64-9552-c74208b740ad"


@pytest.mark.asyncio
async def test_movies_search_too_huge_page(
    session, es_client, movies_index_create, movies_data_load
):
    url_template = "{service_url}/api/v1/films/?page_size=50&page_number=51"
    url = url_template.format(service_url=settings.app_dsn)
    async with session.get(url) as response:
        body = await response.json()
        assert response.status == http.HTTPStatus.OK
        assert len(body) == 0


@pytest.mark.asyncio
async def test_get_movie_by_invalid_id(session, es_client, movies_index_create):
    url_template = "{service_url}/api/v1/films/{id}/"
    id = "aaaaaaaa-1111-2222-3333-bbbbbbbbbbbb"
    url = url_template.format(service_url=settings.app_dsn, id=id)
    async with session.get(url) as response:
        assert response.status == http.HTTPStatus.NOT_FOUND
