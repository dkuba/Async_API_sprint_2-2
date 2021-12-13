from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import UUID4

from api.helper.params import PaginateModel, parse_pagination
from api.schemas import OutputMovieMinimalisticSchema, OutputMovieSchema
from api_cache.cache import cache
from core.config import CACHE_EXPIRE_IN_SECONDS
from services.movie import MovieService, get_movie_service

router = APIRouter()


@router.get(path="/{movie_id:uuid}", response_model=OutputMovieSchema)
@cache(expire=CACHE_EXPIRE_IN_SECONDS)
async def movie_details(
    movie_id: UUID4, movie_service: MovieService = Depends(get_movie_service)
) -> OutputMovieSchema:
    """Получить одну запись Фильма по идентификатору"""

    movie = await movie_service.get_by_id(str(movie_id))

    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="movie not found"
        )

    return OutputMovieSchema.from_es_model(movie)


@router.get(path="/", response_model=list[OutputMovieMinimalisticSchema])
@cache(expire=CACHE_EXPIRE_IN_SECONDS)
async def movie_list(
    filter_genre_id: Optional[UUID4] = Query(None, alias="filter[genre]"),
    sort_param: Optional[str] = Query(None, regex=r"-?imdb_rating$", alias="sort"),
    pagination: PaginateModel = Depends(parse_pagination),
    movie_service: MovieService = Depends(get_movie_service),
) -> list[OutputMovieMinimalisticSchema]:
    """Получить список Фильмов"""

    page = {"size": pagination.page_size, "number": pagination.page_number}

    filters = []
    if filter_genre_id:
        filters.append(
            {"path": "genres", "field": "genres.id", "value": str(filter_genre_id)}
        )

    sort = {}
    if sort_param:
        if sort_param[0] == "-":
            sort["field"] = sort_param[1:]
            sort["direction"] = "desc"
        else:
            sort["field"] = sort_param
            sort["direction"] = "asc"

    movies = await movie_service.get_list(
        page=page,
        filters=filters,
        sort=sort,
    )

    return [OutputMovieMinimalisticSchema.from_es_model(movie) for movie in movies]


@router.get(path="/search", response_model=list[OutputMovieMinimalisticSchema])
@cache(expire=CACHE_EXPIRE_IN_SECONDS)
async def search(
    query: str,
    pagination: PaginateModel = Depends(parse_pagination),
    movie_service: MovieService = Depends(get_movie_service),
) -> list[OutputMovieMinimalisticSchema]:
    """Поиск по Фильмам"""

    page = {"size": pagination.page_size, "number": pagination.page_number}

    movies = await movie_service.get_list(
        query=query,
        page=page,
    )

    return [OutputMovieMinimalisticSchema.from_es_model(movie) for movie in movies]
