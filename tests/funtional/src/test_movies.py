import pytest


@pytest.mark.asyncio
async def test_search_detailed(es_client, make_get_request):
    await es_client.fill_in(fixture="movies_detail.json")

    response = await make_get_request("/film/a801e84c-316a-4c0c-a5a5-cc024234b2cb", {})

    # print(response.body)

    # Заполнение данных для теста

    # # Выполнение запроса
    # response = await make_get_request('/search', {'search': 'Star Wars'})
    
    # Проверка результата
    assert response.status == 200
    assert response.body["uuid"] == "a801e84c-316a-4c0c-a5a5-cc024234b2cb"

    # # assert response.body == expected

    await es_client.clear_out(fixture="movies_detail.json")