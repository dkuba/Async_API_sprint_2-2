"""Модуль содержит карту верхнеуровневых эндпоинтов
и преренаправляет запрос пользователя на Модули-хэндлеры
"""

from fastapi import APIRouter

from api.v1.endpoints import genre, movie, person

api_v1_router = APIRouter()
api_v1_router.include_router(movie.router, prefix="/film", tags=["films"])
api_v1_router.include_router(genre.router, prefix="/genre", tags=["genres"])
api_v1_router.include_router(person.router, prefix="/person", tags=["persons"])
