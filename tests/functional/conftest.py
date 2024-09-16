import aiohttp
import asyncio
import json
import pytest_asyncio
import sys

from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk

from settings import film_test_settings


@pytest_asyncio.fixture(scope='session')
def event_loop():
    if sys.version_info < (3, 10):
        loop = asyncio.get_event_loop()
    else:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()

    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest_asyncio.fixture(name='es_client', scope='session')
async def es_client():
    es_client = AsyncElasticsearch(hosts=film_test_settings.es_host, verify_certs=False)
    yield es_client
    await es_client.close()


@pytest_asyncio.fixture(name='aiohttp_client_session', scope='session')
async def aiohttp_client_session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest_asyncio.fixture(name='es_write_data')
def es_write_data(es_client):
    async def inner(index, mapping, data: list[dict]):
        bulk_query: list[dict] = []
        for row in data:
            data = {"_index": index, "_id": row["id"]}
            data.update({"_source": row})
            bulk_query.append(data)
        if await es_client.indices.exists(index=index):
            await es_client.indices.delete(index=index)
        await es_client.indices.create(index=index, **mapping)

        updated, errors = await async_bulk(client=es_client, actions=bulk_query)

        if errors:
            raise Exception('Ошибка записи данных в Elasticsearch')
    return inner


@pytest_asyncio.fixture(name="make_get_request")
def make_get_request(aiohttp_client_session):
    async def inner(url, query_data=None):
        # async with aiohttp_client_session() as session:
        url = film_test_settings.service_url + url
        print(f"***** query data = {query_data}")
        if query_data:
            params = {
                "query": query_data['search']
            }
            async with aiohttp_client_session.get(
                url,
                params=params
            ) as response:
                body = await response.json(loads=json.loads)
                status = response.status
        else:
            async with aiohttp_client_session.get(
                url,
            ) as response:
                body = await response.json(loads=json.loads)
                status = response.status
        return body, status
    return inner
