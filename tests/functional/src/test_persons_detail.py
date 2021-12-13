import uuid
from http import HTTPStatus
from typing import Callable

import pytest


@pytest.mark.usefixtures("data_setup")
@pytest.mark.data_setup_params("persons", "persons_detail.json")
@pytest.mark.asyncio
class TestPersonDetail:
    async def test_success(self, make_get_request: Callable, uploaded_data):
        response = await make_get_request(
            "/person/{uuid}".format(uuid=uploaded_data["id"]), {}
        )

        assert response.status == HTTPStatus.OK
        assert response.body["uuid"] == uploaded_data["id"]
        assert response.body.get("full_name", None)

    async def test_not_found(self, make_get_request: Callable):
        response = await make_get_request("/person/{uuid}".format(uuid=uuid.uuid4()))

        assert response.status == HTTPStatus.NOT_FOUND
        assert response.body == {"detail": "person not found"}
