import pytest
import time

from testdata import es_mapping, db_data


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
                {'search': 'Howard'},
                {'status': 200, 'length': 1}
        ),
        (
                {'search': 'Yzrqg'},
                {'status': 200, 'length': 0}
        ),
        (
                {'search': ' '},
                {'status': 200, 'length': 0}
        ),
    ]
)
@pytest.mark.asyncio
async def test_person_search(
    es_write_data,
    make_get_request,
    query_data,
    expected_answer
):

    # load data into ES
    await es_write_data(index="movies", mapping=es_mapping.MAPPING_MOVIES, data=db_data.movies_data)
    await es_write_data(index="persons", mapping=es_mapping.MAPPING_PERSONS, data=db_data.persons_data)

    # wait 1 second for index to be ready
    time.sleep(1)

    # make query to ES via API
    body, status = await make_get_request("/api/v1/persons/search", query_data)

    # make asserts
    assert status == expected_answer["status"]
    assert len(body) == expected_answer["length"]


@pytest.mark.parametrize(
    'person_id, expected_answer',
    [
        (
                'b45bd7bc-2e16-46d5-b125-983d356768c6',
                {'status': 200, 'length': 3}
        ),
        (
                'b45bd7bc-2e16-46d5-b125-983d356768c0',
                {'status': 404, 'length': 1}
        ),
    ]
)
@pytest.mark.asyncio
async def test_person_by_id(
    es_write_data,
    make_get_request,
    person_id,
    expected_answer
):

    # load data into ES
    await es_write_data(index="movies", mapping=es_mapping.MAPPING_MOVIES, data=db_data.movies_data)
    await es_write_data(index="persons", mapping=es_mapping.MAPPING_PERSONS, data=db_data.persons_data)

    # wait 1 second for index to be ready
    time.sleep(1)

    # make query to ES via API
    body, status = await make_get_request("/api/v1/persons/" + person_id)

    # make asserts
    assert status == expected_answer["status"]
    assert len(body) == expected_answer["length"]


@pytest.mark.parametrize(
    'person_id, expected_answer',
    [
        (
                'b45bd7bc-2e16-46d5-b125-983d356768c6',
                {'status': 200, 'length': 60}
        ),
        (
                'b45bd7bc-2e16-46d5-b125-983d356768c0',
                {'status': 200, 'length': 0}
        ),
    ]
)
@pytest.mark.asyncio
async def test_person_film(
    es_write_data,
    make_get_request,
    person_id,
    expected_answer
):

    # load data into ES
    await es_write_data(index="movies", mapping=es_mapping.MAPPING_MOVIES, data=db_data.movies_data)
    await es_write_data(index="persons", mapping=es_mapping.MAPPING_PERSONS, data=db_data.persons_data)

    # wait 1 second for index to be ready
    time.sleep(1)

    # make query to ES via API
    body, status = await make_get_request("/api/v1/persons/" + person_id + "/film")

    # make asserts
    assert status == expected_answer["status"]
    assert len(body) == expected_answer["length"]
