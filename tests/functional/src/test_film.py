import asyncio
import pytest
from testdata import es_mapping, db_data

existing_film_id = db_data.movies_data[0]["id"]

@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
            {'search': 'The Star'},
            {'status': 200, 'length': 1}
        ),
        (
            {'search': 'Nonexistent Movie'},
            {'status': 200, 'length': 0}
        ),
        (
            {'search': ' '},
            {'status': 200, 'length': 0}
        ),
    ]
)
@pytest.mark.asyncio
async def test_film_search(
    es_write_data,
    make_get_request,
    query_data,
    expected_answer
):

    await es_write_data(index="movies_test", mapping=es_mapping.MAPPING_MOVIES, data=db_data.movies_data)

    await asyncio.sleep(1)

    body, status = await make_get_request("/api/v1/films/search", query_data)

    assert status == expected_answer["status"]
    assert len(body) == expected_answer["length"]


@pytest.mark.parametrize(
    'film_id, expected_answer',
    [
        (
            existing_film_id,
            {'status': 200, 'length': 1}
        ),
        (
            'nonexistent-film-id',
            {'status': 404, 'length': 0}
        ),
    ]
)
@pytest.mark.asyncio
async def test_film_by_id(
    es_write_data,
    make_get_request,
    film_id,
    expected_answer
):

    await es_write_data(index="movies_test", mapping=es_mapping.MAPPING_MOVIES, data=db_data.movies_data)

    await asyncio.sleep(1)

    body, status = await make_get_request(f"/api/v1/films/{film_id}")

    assert status == expected_answer["status"]
    assert len(body) == expected_answer["length"]


@pytest.mark.parametrize(
    'film_id, expected_answer',
    [
        (
            existing_film_id,
            {'status': 200, 'length': 1}
        ),
        (
            'nonexistent-film-id',
            {'status': 404, 'length': 0}
        ),
    ]
)
@pytest.mark.asyncio
async def test_film_details(
    es_write_data,
    make_get_request,
    film_id,
    expected_answer
):

    await es_write_data(index="movies_test", mapping=es_mapping.MAPPING_MOVIES, data=db_data.movies_data)

    await asyncio.sleep(1)

    body, status = await make_get_request(f"/api/v1/films/{film_id}")

    assert status == expected_answer["status"]
    assert len(body) == expected_answer["length"]
