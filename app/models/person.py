from uuid import UUID

from models.base import OrjsonBaseModel


class PersonFilm(OrjsonBaseModel):
    id: UUID
    roles: list[str]


class Person(OrjsonBaseModel):
    id: UUID
    full_name: str
    films: list[PersonFilm] | None
