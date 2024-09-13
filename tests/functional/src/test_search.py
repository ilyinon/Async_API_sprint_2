import aiohttp
import json
import pytest
import time
import uuid

from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk

from settings import test_settings

#  Название теста должно начинаться со слова `test_`
#  Любой тест с асинхронными вызовами нужно оборачивать декоратором `pytest.mark.asyncio`,
#  который следит за запуском и работой цикла событий.


@pytest.mark.asyncio
async def test_search():

    # 1. Генерируем данные для ES
    es_data = [
        {
            "id": str(uuid.uuid4()),
            "imdb_rating": 8.5,
            "genres": ["Action", "Sci-Fi"],
            "title": "The Star",
            "description": "New World",
            "directors_names": ["Kris", "Stew"],
            "actors_names": ["Ann", "Bob"],
            "writers_names": ["Ben", "Howard"],
            "directors": [
                {"id": "ef86b8ff-3c82-4d31-ad8e-72b69f4e3f91", "name": "Kris"},
                {"id": "fb111f22-121e-44a7-b78f-b19191810fb2", "name": "Stew"},
            ],
            "actors": [
                {"id": "ef86b8ff-3c82-4d31-ad8e-72b69f4e3f95", "name": "Ann"},
                {"id": "fb111f22-121e-44a7-b78f-b19191810fbf", "name": "Bob"},
            ],
            "writers": [
                {"id": "caf76c67-c0fe-477e-8766-3ab3ff2574b5", "name": "Ben"},
                {"id": "b45bd7bc-2e16-46d5-b125-983d356768c6", "name": "Howard"},
            ],
        }
        for _ in range(60)
    ]

    bulk_query: list[dict] = []
    for row in es_data:
        data = {"_index": "movies", "_id": row["id"]}
        data.update({"_source": row})
        bulk_query.append(data)

    # 2. Загружаем данные в ES
    es_client = AsyncElasticsearch(hosts=test_settings.es_host, verify_certs=False)
    if await es_client.indices.exists(index=test_settings.es_index):
        await es_client.indices.delete(index=test_settings.es_index)
    await es_client.indices.create(
        index=test_settings.es_index, **test_settings.es_index_mapping
    )

    updated, errors = await async_bulk(client=es_client, actions=bulk_query)

    await es_client.close()

    if errors:
        raise Exception("Ошибка записи данных в Elasticsearch")

    # 3. Запрашиваем данные из ES по API
    # Подождем 1 секунду, пока эластик сформирует индекс
    time.sleep(1)
    async with aiohttp.ClientSession() as session:
        url = test_settings.service_url + "/api/v1/films/search"
        query_data = {
            "query": "Star"
        }
        headers = {
            'User-Agent': 'Mozilla'
        }
        async with session.get(
            url,
            params=query_data,
            headers=headers
        ) as response:
            body = await response.json(loads=json.loads)
            headers = response.headers
            status = response.status
            print(f"**** headers: {headers}")
            print(f"**** status: {status}")
            print(f"**** url: {response.url}")
            print(f"**** body: {body}")
        await session.close()

    # 4. Проверяем ответ

    assert status == 200
    assert len(body) == 50
