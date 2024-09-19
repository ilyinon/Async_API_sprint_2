pytest_plugins = "tests.fixtures"

import asyncio
import json

import aiohttp
import pytest
import pytest_asyncio
from elasticsearch import Elasticsearch

from tests.functional.settings import settings
from tests.functional.testdata.elastic import GENRE_INDEX, MOVIES_INDEX, PERSON_INDEX
from tests.functional.testdata.genres import GENRES_DATA
from tests.functional.testdata.movies import MOVIES_DATA
from tests.functional.testdata.persons import PERSONS_DATA

TEST_GENRES = settings.genres_index
TEST_PERSONS = settings.persons_index
TEST_MOVIES = settings.movies_index


def get_str_query(index, data):
    bulk_query = []
    for row in data:
        bulk_query.extend(
            [
                json.dumps({"index": {"_index": index, "_id": row["id"]}}),
                json.dumps(row),
            ]
        )
    return "\n".join(bulk_query) + "\n"


@pytest.fixture(scope="session")
def es_client():
    es_client = Elasticsearch(settings.elastic_dsn)

    yield es_client
    es_client.close()


@pytest.fixture
def movies_index_create(es_client):
    es_client.indices.create(index=TEST_MOVIES, ignore=400, body=MOVIES_INDEX)
    yield es_client

    es_client.indices.delete(index=TEST_MOVIES)


@pytest.fixture
def genres_index_create(es_client):
    es_client.indices.create(index=TEST_GENRES, ignore=400, body=GENRE_INDEX)
    yield es_client
    es_client.indices.delete(index=TEST_GENRES)


@pytest.fixture
def persons_index_create(es_client):
    es_client.indices.create(index=TEST_PERSONS, ignore=400, body=PERSON_INDEX)
    yield es_client
    es_client.indices.delete(index=TEST_PERSONS)


@pytest.fixture
def movies_data_load(es_client, movies_index_create):
    str_query = get_str_query(TEST_MOVIES, MOVIES_DATA)
    es_client.bulk(str_query, refresh=True)
    yield es_client


@pytest.fixture
def persons_data_load(es_client, persons_index_create):
    str_query = get_str_query(TEST_PERSONS, PERSONS_DATA)
    es_client.bulk(str_query, refresh=True)
    yield es_client


@pytest.fixture
def genres_data_load(es_client, genres_index_create):
    str_query = get_str_query(TEST_GENRES, GENRES_DATA)
    es_client.bulk(str_query, refresh=True)
    yield es_client