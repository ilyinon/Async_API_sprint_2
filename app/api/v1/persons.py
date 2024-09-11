from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from models.base import OrjsonBaseModel
from services.person import PersonService, get_person_service

router = APIRouter()


class PersonFilm(OrjsonBaseModel):
    uuid: UUID  # ID of film
    roles: list[str]


class Film(OrjsonBaseModel):
    uuid: UUID
    title: str
    imdb_rating: float | None


class Person(OrjsonBaseModel):
    uuid: UUID
    full_name: str
    films: list[PersonFilm]


@router.get(
    '/search',
    response_model=list[Person],
    summary='Поиск по персонажам',
    description='Получить список персонажей, отвечающих условиям запроса'
)
async def person_search_list(
    person_service: PersonService = Depends(get_person_service),
    page_size: Annotated[int, Query(description="Персонажей на страницу", ge=1)] = 50,
    page_number: Annotated[int, Query(description="Номер страницы", ge=1)] = 1,
    query: Annotated[str, Query(description="Запрос")] = "Query"
):
    persons = await person_service.get_search_list(query, page_number, page_size)
    persons_response = []
    for person in persons:
        films = []
        for film in person.films:
            films.append(PersonFilm(uuid=film.id, roles=film.roles))
        persons_response.append(Person(uuid=person.id, full_name=person.full_name, films=films))
    return persons_response


@router.get(
    '/{person_id}/film',
    response_model=list[Film],
    summary='Фильмы по персонажам',
    description='Получить список фильмов, в которых участвовала персона'
)
async def person_film_list(
    person_id: UUID,
    person_service: PersonService = Depends(get_person_service)
):
    films = await person_service.get_person_film_list(person_id)

    return [
        Film(uuid=film.id, title=film.title, imdb_rating=film.imdb_rating)
        for film in films
    ]


@router.get(
    '/{person_id}',
    response_model=Person,
    summary='Страница персонажа',
    description='Данные по конкретному персонажу'
)
async def person_details(person_id: UUID, person_service: PersonService = Depends(get_person_service)) -> Person:
    person = await person_service.get_by_id(person_id)

    if not person:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail=f"person with id {person_id} not found"
        )
    films = []
    for film in person.films:
        films.append(PersonFilm(uuid=film.id, roles=film.roles))

    return Person(uuid=person.id, full_name=person.full_name, films=films)
