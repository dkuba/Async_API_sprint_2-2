from http import HTTPStatus
from typing import Callable

import pytest


@pytest.mark.usefixtures("data_setup")
@pytest.mark.data_setup_params("persons", "persons_list.json")
@pytest.mark.asyncio
class TestPersonsList:
    async def test_success(self, make_get_request: Callable):
        response = await make_get_request("/person", {})

        assert response.status == HTTPStatus.OK
        assert response.body[0].get("full_name", None)
        assert len(response.body) == 30

    async def test_check_paging_out_of_range(self, make_get_request: Callable):
        response = await make_get_request(
            "/person", {"page[number]": 2, "page[size]": 30}
        )

        assert response.status == HTTPStatus.OK
        assert len(response.body) == 0

    async def test_check_paging_page_size(self, make_get_request: Callable):
        response = await make_get_request(
            "/person", {"page[number]": 5, "page[size]": 5}
        )

        assert response.status == HTTPStatus.OK
        assert len(response.body) == 5
