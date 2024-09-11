from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from models.base import OrjsonBaseModel
from services.genre import GenreService, get_genre_service

router = APIRouter()


class Genre(OrjsonBaseModel):
    uuid: UUID
    name: str


@router.get(
    '',
    response_model=list[Genre],
    summary='Список жанров',
    description='Получить список жанров'
)
async def genre_list(
    genre_service: GenreService = Depends(get_genre_service),
    page_size: Annotated[int, Query(description="Жанров на страницу", ge=1)] = 50,
    page_number: Annotated[int, Query(description="Номер страницы", ge=1)] = 1,
):
    genres = await genre_service.get_list(page_number, page_size)
    return [
        Genre(uuid=genre.id, name=genre.name)
        for genre in genres
    ]


@router.get(
    '/{genre_id}',
    response_model=Genre,
    summary="Страница жанра",
    description="Данные по конкретному жанру",
)
async def genre_details(genre_id: UUID, genre_service: GenreService = Depends(get_genre_service)) -> Genre:
    genre = await genre_service.get_by_id(genre_id)

    if not genre:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail=f"genre with id {genre_id} not found"
        )

    return Genre(uuid=genre.id, name=genre.name)
