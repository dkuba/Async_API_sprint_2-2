"""Классы описывающие модель данных Жанр. Данные хранятся в ElasticSearch
"""

from pydantic import UUID4

from models.base import BaseElasticModel


class Genre(BaseElasticModel):
    """Модель жанра"""

    id: UUID4
    name: str
