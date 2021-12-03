from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import UUID4

from api.helper.params import PaginateModel, parse_pagination
from api.schemas import OutputGenreSchema
from api_cache.cache import cache
from services.genre import GenreService, get_genre_service

router = APIRouter()


@router.get(path="/", response_model=List[OutputGenreSchema])
@cache(expire=10)
async def genre_list(
    pagination: PaginateModel = Depends(parse_pagination),
    genre_service: GenreService = Depends(get_genre_service),
) -> List[OutputGenreSchema]:

    genres = await genre_service.get_list(
        page={"size": pagination.page_size, "number": pagination.page_number},
    )

    return [OutputGenreSchema.from_es_model(genre) for genre in genres]


@router.get(
    path="/{genre_id}",
    response_model=OutputGenreSchema,
)
@cache(expire=10)
async def genre_detail(
    genre_id: UUID4, genre_service: GenreService = Depends(get_genre_service)
) -> OutputGenreSchema:
    genre = await genre_service.get_by_id(str(genre_id))

    if not genre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="genre not found"
        )

    return OutputGenreSchema.from_es_model(genre)
