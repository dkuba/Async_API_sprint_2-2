import orjson
from pydantic import BaseModel


def orjson_dumps(v, *, default):
    """Десериализатор объекта в json строку"""
    return orjson.dumps(v, default=default).decode()


class BaseAPISchema(BaseModel):
    """Базовый класс для всех Схем данных API.
    Переопределён сериализатор/десериализатор
    """

    class Config:
        """Конфиг"""

        json_loads = orjson.loads
        json_dumps = orjson_dumps
