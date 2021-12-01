from pydantic import UUID4

from api.schemas.base import BaseAPISchema
from models.genre import Genre


class OutputGenreSchema(BaseAPISchema):
    """Полное описание Жанра"""

    uuid: UUID4
    name: str

    @classmethod
    def from_es_model(cls, genre: Genre):
        return cls(uuid=genre.id, name=genre.name)


class OutputGenreMinimalisticSchema(OutputGenreSchema):
    """Минимальистичное описание Жанра"""

    pass
