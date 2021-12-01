from typing import List

from pydantic import UUID4

from api.schemas.base import BaseAPISchema
from models.person import Person


class OutputMoviePersonRoleMinimalisticSchema(BaseAPISchema):
    """Минималистичное описание Фильма + роль Персоны"""

    uuid: UUID4
    title: str
    person_role: str


class OutputPersonSchema(BaseAPISchema):
    """Описание Персоны и её фильмов"""

    uuid: UUID4
    full_name: str
    films: List[OutputMoviePersonRoleMinimalisticSchema]

    @classmethod
    def from_es_model(cls, person: Person):
        return cls(
            uuid=person.id,
            full_name=person.full_name,
            films=[
                OutputMoviePersonRoleMinimalisticSchema(
                    uuid=movie.id,
                    title=movie.title,
                    person_role=movie.person_role,
                )
                for movie in person.movies
            ],
        )
