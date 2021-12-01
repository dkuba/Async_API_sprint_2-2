from typing import Optional

import orjson
from fastapi import Query
from pydantic import BaseModel

from core import config


def orjson_dumps(v, *, default):
    """Десериализатор объекта в json строку"""
    return orjson.dumps(v, default=default).decode()


class PaginateModel(BaseModel):
    """Класс описывающий входные параметры API отвечающие за
    постраничную разбивку выходных данных
    """

    page_number: int = config.DEFAULT_PAGE_NUMBER
    page_size: int = config.DEFAULT_PAGE_SIZE

    class Config:
        """Конфиг"""

        json_loads = orjson.loads
        json_dumps = orjson_dumps


async def parse_pagination(
    page_number: Optional[int] = Query(
        config.DEFAULT_PAGE_NUMBER,
        alias="page[number]",
        description="Page number for pagination",
    ),
    page_size: Optional[int] = Query(
        config.DEFAULT_PAGE_SIZE,
        alias="page[size]",
        description="Items amount on page",
    ),
):
    return PaginateModel(
        page_number=int(page_number),
        page_size=int(page_size),
    )
