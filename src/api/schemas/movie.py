from pydantic import UUID4

from api.schemas.base import BaseAPISchema
from api.schemas.genre import OutputGenreMinimalisticSchema
from models.movie import Movie


class OutputPersonMinimalisticSchema(BaseAPISchema):
    """Минималистичное описание Персон"""

    uuid: UUID4
    full_name: str


class OutputMovieSchema(BaseAPISchema):
    """Полное описание Фильма"""

    uuid: UUID4
    title: str
    imdb_rating: float
    description: str
    genres: list[OutputGenreMinimalisticSchema]
    actors: list[OutputPersonMinimalisticSchema]
    writers: list[OutputPersonMinimalisticSchema]
    directors: list[OutputPersonMinimalisticSchema]

    @classmethod
    def from_es_model(cls, movie: Movie):
        return cls(
            uuid=movie.id,
            title=movie.title,
            description=movie.description,
            imdb_rating=movie.imdb_rating,
            genres=[
                OutputGenreMinimalisticSchema(
                    uuid=genre.id,
                    name=genre.name,
                )
                for genre in movie.genres
            ],
            actors=[
                OutputPersonMinimalisticSchema(
                    uuid=person.id,
                    full_name=person.name,
                )
                for person in movie.actors
            ],
            directors=[
                OutputPersonMinimalisticSchema(
                    uuid=person.id,
                    full_name=person.name,
                )
                for person in movie.directors
            ],
            writers=[
                OutputPersonMinimalisticSchema(
                    uuid=person.id,
                    full_name=person.name,
                )
                for person in movie.writers
            ],
        )


class OutputMovieMinimalisticSchema(BaseAPISchema):
    """Минималистичное описание Фильма"""

    uuid: UUID4
    title: str
    imdb_rating: float

    @classmethod
    def from_es_model(cls, movie: Movie):
        return cls(
            uuid=movie.id,
            title=movie.title,
            imdb_rating=movie.imdb_rating,
        )
