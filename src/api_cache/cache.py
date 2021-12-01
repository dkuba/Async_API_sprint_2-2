import json
from functools import wraps
from typing import Callable, Optional

from fastapi.encoders import jsonable_encoder


class JsonEncoder(json.JSONEncoder):
    def default(self, obj):
        return jsonable_encoder(obj)


class APICache:
    _backend = None
    _prefix = None

    @classmethod
    def init(cls, backend, prefix: str = ""):
        cls._backend = backend
        cls._prefix = prefix

    @classmethod
    def get_backend(cls):
        assert cls._backend, "You must call init first!"
        return cls._backend

    @classmethod
    def get_prefix(cls):
        assert cls._prefix, "You must call init first!"
        return cls._prefix


def default_key_builder(
    func,
    namespace: Optional[str] = "",
    *args,
    **kwargs,
):
    prefix = APICache.get_prefix()
    cache_key = (
        f"{prefix}:{namespace}:{func.__module__}:{func.__name__}:{args}:{kwargs}"
    )
    return cache_key


def cache(
    expire: int = None,
    key_builder: Callable = default_key_builder,
    namespace: Optional[str] = "",
):
    """
    cache all function
    :param expire:
    :param coder:
    :param key_builder:
    :param namespace:
    :return:
    """

    def wrapper(func):
        @wraps(func)
        async def inner(*args, **kwargs):
            backend = APICache.get_backend()
            cache_key = key_builder(func, namespace, *args, **kwargs)
            ret = await backend.get(cache_key)
            if ret is not None:
                return json.loads(ret)

            ret = await func(*args, **kwargs)
            await backend.set(cache_key, json.dumps(ret, cls=JsonEncoder), expire)
            return ret

        return inner

    return wrapper
