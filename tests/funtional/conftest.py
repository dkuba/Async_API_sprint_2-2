import asyncio
from dataclasses import dataclass

import aiohttp
import aioredis
import pytest
from multidict import CIMultiDictProxy
from settings import settings
from utils.es_helper import ESHelper

es_helper = ESHelper()


@dataclass
class HTTPResponse:
    body: dict
    headers: CIMultiDictProxy[str]
    status: int


@pytest.fixture(scope="session", autouse=True)
async def es_setup():
    await es_helper.init_indices()
    yield
    await es_helper.delete_indices()


@pytest.fixture(scope="session")
async def session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def redis_client():
    redis = await aioredis.create_redis_pool((settings.Redis.HOST, settings.Redis.PORT))
    yield redis
    redis.close()
    await redis.wait_closed()


@pytest.fixture(scope="function", autouse=True)
async def clear_cache(redis_client):
    await redis_client.flushall()
    yield
    await redis_client.flushall()


@pytest.fixture(scope="class")
async def data_setup(request: pytest.FixtureRequest):
    marker = request.node.get_closest_marker("data_setup_params")
    if marker is not None:
        index_name = marker.args[0]
        file_name = marker.args[1]
        await es_helper.fill_in(fixture=file_name, index_name=index_name)
        yield
        await es_helper.clear_out(fixture=file_name, index_name=index_name)


@pytest.fixture(scope="class")
async def uploaded_data(request: pytest.FixtureRequest):
    marker = request.node.get_closest_marker("data_setup_params")
    if marker is not None:
        file_name = marker.args[1]
        yield es_helper.read_file(file_name)


@pytest.fixture
def make_get_request(session):
    async def inner(method: str, params: dict = None) -> HTTPResponse:
        params = params or {}
        url = (
            settings.SERVICE_URL + "/api/v1" + method
        )  # в боевых системах старайтесь так не делать!
        async with session.get(url, params=params) as response:
            return HTTPResponse(
                body=await response.json(),
                headers=response.headers,
                status=response.status,
            )

    return inner
