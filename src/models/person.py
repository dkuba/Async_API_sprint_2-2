"""Классы описывающие модель данных Персона. Данные хранятся в ElasticSearch
"""

from pydantic import UUID4

from models.base import BaseElasticModel


class PersonMovies(BaseElasticModel):
    """Модель Фильмов, вложенных в структуру Персон"""

    id: UUID4
    title: str
    person_role: str


class Person(BaseElasticModel):
    """Модель Персоны"""

    id: UUID4
    full_name: str
    movies: list[PersonMovies]
