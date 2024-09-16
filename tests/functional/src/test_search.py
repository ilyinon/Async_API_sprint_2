import pytest
import time
import uuid

from testdata import es_mapping


#  Название теста должно начинаться со слова `test_`
#  Любой тест с асинхронными вызовами нужно оборачивать декоратором `pytest.mark.asyncio`,
#  который следит за запуском и работой цикла событий.


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
                {'search': 'The Star'},
                {'status': 200, 'length': 50}
        ),
        (
                {'search': 'Mashed potato'},
                {'status': 200, 'length': 0}
        )
    ]
)
@pytest.mark.asyncio
async def test_search(es_write_data, make_get_request, query_data, expected_answer):
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
    # 2. Загружаем данные в ES
    await es_write_data(index="movies", mapping=es_mapping.MAPPING_MOVIES, data=es_data)

    # *** Подождем 1 секунду, пока эластик сформирует индекс
    time.sleep(1)

    # 3. Запрашиваем данные из ES по API
    body, status = await make_get_request("/api/v1/films/search", query_data)

    # 4. Проверяем ответ

    assert status == expected_answer["status"]
    assert len(body) == expected_answer["length"]


# import pytest
# from testdata.db_data import movies_data
# from settings import film_test_settings

# @pytest.mark.asyncio
# async def test_es_index_creation(es_client, es_write_data):
#     # Use the fixture to write data to Elasticsearch
#     await es_write_data(
#         index=film_test_settings.es_index,
#         mapping=film_test_settings.es_index_mapping,
#         data=movies_data
#     )

#     # Verify that the index was created
#     index_exists = await es_client.indices.exists(index=film_test_settings.es_index)
#     assert index_exists, "Elasticsearch index was not created"

# @pytest.mark.asyncio
# async def test_es_data_insertion(es_client, es_write_data):
#     # Use the fixture to write data to Elasticsearch
#     await es_write_data(
#         index=film_test_settings.es_index,
#         mapping=film_test_settings.es_index_mapping,
#         data=movies_data
#     )

#     # Verify that the data was inserted
#     for movie in movies_data:
#         doc_id = movie['id']
#         document = await es_client.get(index=film_test_settings.es_index, id=doc_id)
#         assert document['_source']['title'] == movie['title'], f"Document with ID {doc_id} has incorrect data"

# @pytest.mark.asyncio
# async def test_es_search(es_client, es_write_data, make_get_request):
#     # Write data to Elasticsearch
#     await es_write_data(
#         index=film_test_settings.es_index,
#         mapping=film_test_settings.es_index_mapping,
#         data=movies_data
#     )

#     # Perform a search query
#     query_data = {
#         "search": {
#             "query": {
#                 "match": {
#                     "title": "The Star"
#                 }
#             }
#         }
#     }
#     response_body, response_status = await make_get_request('/search', query_data)
    
#     assert response_status == 200, f"Unexpected status code: {response_status}"
#     assert 'hits' in response_body, "Response does not contain 'hits'"
#     assert len(response_body['hits']['hits']) > 0, "No documents found in search results"
#     assert response_body['hits']['hits'][0]['_source']['title'] == "The Star", "Search result does not match expected title"
