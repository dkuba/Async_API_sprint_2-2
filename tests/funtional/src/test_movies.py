import uuid
from typing import Callable

import pytest


@pytest.mark.usefixtures("data_setup")
@pytest.mark.data_setup_params("movies", "movies_detail.json")
@pytest.mark.asyncio
class TestMoviesDetail:
    async def test_success(self, make_get_request: Callable, uploaded_data):
        response = await make_get_request(
            "/film/{uuid}".format(uuid=uploaded_data["id"]), {}
        )

        assert response.status == 200
        assert response.body["uuid"] == uploaded_data["id"]
        assert len(response.body["genres"]) == 2
        assert len(response.body["directors"]) == 1
        assert len(response.body["actors"]) == 0
        assert len(response.body["writers"]) == 0

    async def test_not_found(self, make_get_request: Callable):
        response = await make_get_request("/film/{uuid}".format(uuid=uuid.uuid4()))

        assert response.status == 404
        assert response.body == {"detail": "movie not found"}
