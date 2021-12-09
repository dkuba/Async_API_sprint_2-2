from typing import Callable

import pytest


@pytest.mark.usefixtures("data_setup")
@pytest.mark.data_setup_params("movies", "movies_list.json")
@pytest.mark.asyncio
class TestMoviesList:
    async def test_success(self, make_get_request: Callable):
        response = await make_get_request("/film", {})

        assert response.status == 200
        assert response.body[0].get("imdb_rating", None)
        assert response.body[0].get("title", None)
        assert len(response.body) == 50

    async def test_check_paging_out_of_range(self, make_get_request: Callable):
        response = await make_get_request(
            "/film", {"page[number]": 2, "page[size]": 50}
        )

        assert response.status == 200
        assert len(response.body) == 0

    async def test_check_paging_page_size(self, make_get_request: Callable):
        response = await make_get_request("/film", {"page[number]": 5, "page[size]": 3})

        assert response.status == 200
        assert len(response.body) == 3

    async def test_check_filter_genre_id(self, make_get_request: Callable):
        response = await make_get_request(
            "/film", {"filter[genre]": "faf1501b-009a-415b-8137-8be5b7a28e0a"}
        )

        assert response.status == 200
        assert len(response.body) == 14

    async def test_check_sort_imdb_rating_asc(self, make_get_request: Callable):
        response = await make_get_request("/film", {"sort": "imdb_rating"})

        assert response.status == 200
        assert len(response.body) == 50
        assert all(
            x["imdb_rating"] <= y["imdb_rating"]
            for x, y in zip(response.body, response.body[1:])
        )

    async def test_check_sort_imdb_rating_desc(self, make_get_request: Callable):
        response = await make_get_request("/film", {"sort": "-imdb_rating"})

        assert response.status == 200
        assert len(response.body) == 50
        assert all(
            x["imdb_rating"] >= y["imdb_rating"]
            for x, y in zip(response.body, response.body[1:])
        )
