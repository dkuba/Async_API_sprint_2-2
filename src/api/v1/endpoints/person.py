from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import UUID4

from api.helper.params import PaginateModel, parse_pagination
from api.schemas import OutputMovieMinimalisticSchema, OutputPersonSchema
from api_cache.cache import cache
from services.movie import MovieService, get_movie_service
from services.person import PersonService, get_person_service

router = APIRouter()


@router.get(path="/", response_model=List[OutputPersonSchema])
@cache(expire=10)
async def person_list(
    pagination: PaginateModel = Depends(parse_pagination),
    person_service: PersonService = Depends(get_person_service),
) -> List[OutputPersonSchema]:

    persons = await person_service.get_list(
        page={"size": pagination.page_size, "number": pagination.page_number},
    )

    return [OutputPersonSchema.from_es_model(person) for person in persons]


@router.get(path="/search", response_model=List[OutputPersonSchema])
@cache(expire=10)
async def person_search(
    query: str,
    pagination: PaginateModel = Depends(parse_pagination),
    person_service: PersonService = Depends(get_person_service),
) -> List[OutputPersonSchema]:

    persons = await person_service.get_list(
        query=query,
        page={"size": pagination.page_size, "number": pagination.page_number},
    )

    return [OutputPersonSchema.from_es_model(person) for person in persons]


@router.get(
    path="/{person_id:uuid}",
    response_model=OutputPersonSchema,
)
@cache(expire=10)
async def person_detail(
    person_id: UUID4, person_service: PersonService = Depends(get_person_service)
) -> OutputPersonSchema:
    person = await person_service.get_by_id(str(person_id))

    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="person not found"
        )

    return OutputPersonSchema.from_es_model(person)


@router.get(
    path="/{person_id:uuid}/film",
    response_model=List[OutputMovieMinimalisticSchema],
)
@cache(expire=10)
async def person_films(
    person_id: UUID4, movie_service: MovieService = Depends(get_movie_service)
) -> List[OutputMovieMinimalisticSchema]:
    movies = await movie_service.get_list_by_person_id(person_id)

    return [OutputMovieMinimalisticSchema.from_es_model(movie) for movie in movies]
