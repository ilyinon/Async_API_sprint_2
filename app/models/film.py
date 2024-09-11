from uuid import UUID

from models.base import OrjsonBaseModel
from models.genre import Genre


class Film(OrjsonBaseModel):
    id: UUID
    title: str
    imdb_rating: float | None


class FilmPerson(OrjsonBaseModel):
    id: UUID
    full_name: str


class FilmDetail(Film):
    description: str
    genres: list[Genre]
    actors: list[FilmPerson]
    writers: list[FilmPerson]
    directors: list[FilmPerson]
