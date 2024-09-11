from http import HTTPStatus
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from app.main import app
from app.models.film import Film, FilmDetail
from app.services.film import FilmService
from fastapi.testclient import TestClient


@pytest.fixture
def mock_film_service():
    """Mock FilmService for dependency injection."""
    mock_service = AsyncMock(spec=FilmService)
    return mock_service


@pytest.fixture
def client(mock_film_service):
    """Fixture for test client with mock dependencies."""
    app.dependency_overrides[FilmService] = lambda: mock_film_service
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_films_list(client, mock_film_service):
    """Test the /films/ endpoint to list films."""
    # Mock data
    film_id = uuid4()
    mock_film_service.get_list.return_value = [
        Film(id=film_id, title="Test Movie", imdb_rating=7.5)
    ]

    response = client.get("/films/")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == [
        {"uuid": str(film_id), "title": "Test Movie", "imdb_rating": 7.5}
    ]

    mock_film_service.get_list.assert_called_once()


@pytest.mark.asyncio
async def test_search_film(client, mock_film_service):
    """Test the /films/search endpoint for searching films."""
    film_id = uuid4()
    mock_film_service.search_film.return_value = [
        Film(id=film_id, title="Search Test Movie", imdb_rating=8.0)
    ]

    response = client.get("/films/search", params={"query": "test"})

    assert response.status_code == HTTPStatus.OK
    assert response.json() == [
        {"uuid": str(film_id), "title": "Search Test Movie", "imdb_rating": 8.0}
    ]

    mock_film_service.search_film.assert_called_once_with("test", 50, 1)


@pytest.mark.asyncio
async def test_film_details(client, mock_film_service):
    """Test the /films/{film_id} endpoint for film details."""
    film_id = uuid4()
    mock_film_service.get_by_id.return_value = FilmDetail(
        id=film_id,
        title="Film Detail Test",
        imdb_rating=7.9,
        description="A great film",
        genres=[{"id": str(uuid4()), "name": "Drama"}],
        actors=[{"id": str(uuid4()), "full_name": "John Doe"}],
        writers=[{"id": str(uuid4()), "full_name": "Jane Doe"}],
        directors=[{"id": str(uuid4()), "full_name": "Director Name"}],
    )

    response = client.get(f"/films/{film_id}")

    assert response.status_code == HTTPStatus.OK
    response_json = response.json()
    assert response_json["id"] == str(film_id)
    assert response_json["title"] == "Film Detail Test"
    assert response_json["imdb_rating"] == 7.9
    assert response_json["description"] == "A great film"
    assert response_json["genres"][0]["name"] == "Drama"

    mock_film_service.get_by_id.assert_called_once_with(film_id)


@pytest.mark.asyncio
async def test_film_details_not_found(client, mock_film_service):
    """Test the /films/{film_id} endpoint when film is not found."""
    film_id = uuid4()
    mock_film_service.get_by_id.return_value = None

    response = client.get(f"/films/{film_id}")

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {
        "detail": f"film with id {film_id} not found"
    }

    mock_film_service.get_by_id.assert_called_once_with(film_id)
