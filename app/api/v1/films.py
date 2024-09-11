from http import HTTPStatus
from typing import Annotated, List, Literal
from uuid import UUID

from core import config
from core.logger import logger
from fastapi import APIRouter, Depends, HTTPException, Query
from models.base import OrjsonBaseModel
from pydantic import BaseModel
from services.film import FilmService, get_film_service

router = APIRouter()


class FilmResponse(OrjsonBaseModel):
    uuid: UUID
    title: str
    imdb_rating: float | None


class PersonResponse(BaseModel):
    id: str | None
    full_name: str


class GenreResponse(BaseModel):
    id: str | None
    name: str


class FilmDetailResponse(BaseModel):
    id: str
    title: str
    imdb_rating: float | None = None
    description: str | None = None
    genres: List[GenreResponse]
    actors: List[PersonResponse]
    writers: List[PersonResponse]
    directors: List[PersonResponse]


@router.get(
    "/",
    response_model=list[FilmResponse],
    summary="Список фильмов",
    description="Получить список фильмов",
)
async def films_list(
    sort: Annotated[
        list[Literal["imdb_rating", "-imdb_rating"]],
        Query(description="Sort by imdb_rating"),
    ] = [],
    genre: Annotated[UUID | None, Query(description="Filter by genre UUID")] = None,
    film_service: FilmService = Depends(get_film_service),
    page_size: Annotated[int, Query(description="Фильмов на страницу", ge=1)] = 50,
    page_number: Annotated[int, Query(description="Номер страницы", ge=1)] = 1,
) -> List[FilmResponse]:
    films = await film_service.get_list(sort, genre, page_size, page_number)
    return [
        FilmResponse(uuid=film.id, title=film.title, imdb_rating=film.imdb_rating)
        for film in films
    ]


@router.get(
    "/search",
    response_model=list[FilmResponse],
    summary="Поиск фильмов",
    description="Получить список найденных фильмов",
)
async def search_film(
    query: Annotated[str, Query(description="Запрос")],
    film_service: FilmService = Depends(get_film_service),
    page_size: Annotated[int, Query(description="Фильмов на страницу", ge=1)] = 50,
    page_number: Annotated[int, Query(description="Номер страницы", ge=1)] = 1,
):
    films = await film_service.search_film(query, page_size, page_number)
    return [
        FilmResponse(uuid=film.id, title=film.title, imdb_rating=film.imdb_rating)
        for film in films
    ]


@router.get(
    "/{film_id}",
    response_model=FilmDetailResponse,
    summary="Информация по фильму",
    description="Полная информация по фильму",
)
async def genre_details(
    film_id: UUID, film_service: FilmService = Depends(get_film_service)
) -> FilmDetailResponse:
    film_detail = await film_service.get_by_id(film_id)

    if not film_detail:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail=f"film with id {film_id} not found"
        )

    return FilmDetailResponse(
        id=str(film_detail.id),
        title=film_detail.title,
        imdb_rating=film_detail.imdb_rating,
        description=film_detail.description,
        genres=[
            GenreResponse(id=str(genre.id), name=genre.name)
            for genre in film_detail.genres
        ],
        actors=[
            PersonResponse(id=str(actor.id), full_name=actor.full_name)
            for actor in film_detail.actors
        ],
        writers=[
            PersonResponse(id=str(writer.id), full_name=writer.full_name)
            for writer in film_detail.writers
        ],
        directors=[
            PersonResponse(id=str(director.id), full_name=director.full_name)
            for director in film_detail.directors
        ],
    )
