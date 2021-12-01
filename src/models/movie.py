"""Классы описывающие модель данных Фильм. Данные хранятся в ElasticSearch
"""

from typing import List

from pydantic import UUID4

from models.base import BaseElasticModel


class Genre(BaseElasticModel):
    """Модель Жанра"""

    id: UUID4
    name: str


class Person(BaseElasticModel):
    """Модель всех Персон: актёра, режисёра, сценариста"""

    id: UUID4
    name: str


class Movie(BaseElasticModel):
    """Модель Фильма"""

    id: UUID4
    title: str
    imdb_rating: float
    description: str
    genres: List[Genre]
    actors: List[Person]
    writers: List[Person]
    directors: List[Person]
