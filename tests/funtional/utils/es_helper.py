import json

from elasticsearch import AsyncElasticsearch
from settings import settings

class ESHelper:
    def __init__(self) -> None:
        self.client = AsyncElasticsearch(hosts=settings.ES.get_dsl)

        # self._movies_index_name = f"test_movies_{self._instance_key}"
        self._movies_index_name = "movies"

    def get_client(self) -> AsyncElasticsearch:
        return self.client

    # def delete_movies_test_index(self):
    #     self.client.indices.delete(self._movies_index_name)

    async def init_indices(self):
        indices = ("movies", "genres", "persons")

        for index_name in indices:
            if not self.client.indices.exists(index_name):
                with open(f"testdata/es_indexes/{index_name}.json") as file:
                    es_index_data = json.load(file)

                await self.client.indices.create(self._movies_index_name, body=es_index_data)

    # async def create_movies_test_index(self):
    #     print("=== OK === ")

    #     with open("testdata/es_indexes/movies.json") as file:
    #         es_index_data = json.load(file)

    #     await self.client.indices.create(self._movies_index_name, body=es_index_data)

    # def create_genres_test_index(self):
    #     pass

    # def create_persons_test_index(self):
    #     pass

    async def fill_in(self, fixture: str):
        with open(f"testdata/fixtures/{fixture}") as file:
            data = json.load(file)

        body = "\n" + json.dumps({"index": {"_index": self._movies_index_name, "_id": data["id"]}}) + "\n" + json.dumps(data) + "\n"

        await self.client.bulk(body, index=self._movies_index_name)

    async def clear_out(self, fixture: str):
        with open(f"testdata/fixtures/{fixture}") as file:
            data = json.load(file)

        if isinstance(data, dict):
            data = [data]
        elif isinstance(data, list):
            pass
        else:
            data = []

        for item in data:
            print(" == delete " + item["id"])
            self.client.delete(self._movies_index_name, item["id"])
            # self.client.indices.delete(self._movies_index_name, item["id"], refresh=True)

    def __enter__(self):
        return self

    def __exit__(self, exct_type, exce_value, traceback):
        # self.delete_movies_test_index()
        self.client.close()