import uuid
from typing import Callable

import pytest


@pytest.mark.usefixtures("data_setup")
@pytest.mark.data_setup_params("movies", "movies_list.json")
@pytest.mark.asyncio
class TestPersonDetail:
    async def test_success(self, make_get_request: Callable):
        response = await make_get_request(
            "/person/{uuid}/film".format(uuid="9b38fe80-3042-4325-a28f-5ab01fdb8b32"), {}
        )

        assert response.status == 200
        assert len(response.body) == 22
        assert response.body[0].get("uuid", None)
        assert response.body[0].get("title", None)
        assert response.body[0].get("imdb_rating", None)

    async def test_not_found(self, make_get_request: Callable):
        response = await make_get_request("/person/{uuid}/film".format(uuid=uuid.uuid4()))

        assert response.status == 200
        assert len(response.body) == 0
