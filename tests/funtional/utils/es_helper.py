import json

from elasticsearch import AsyncElasticsearch
from settings import settings


class ESHelper:
    def __init__(self) -> None:
        self.client = AsyncElasticsearch(hosts=settings.ES.get_dsl)

        self._indices = ("movies", "genres", "persons")

    def get_client(self) -> AsyncElasticsearch:
        return self.client

    async def init_indices(self):
        for index_name in self._indices:
            if not await self.client.indices.exists(index_name):
                with open(f"testdata/es_indexes/{index_name}.json") as file:
                    es_index_data = json.load(file)

                await self.client.indices.create(index_name, body=es_index_data)

    async def delete_indices(self):
        for index_name in self._indices:
            await self.client.indices.delete(index_name, ignore=[400, 404])

    def read_file(self, file_name: str):
        with open(f"testdata/fixtures/{file_name}") as file:
            data = json.load(file)

        return data

    async def fill_in(self, fixture: str, index_name: str):
        data = self.read_file(fixture)

        body = (
            "\n"
            + json.dumps({"index": {"_index": index_name, "_id": data["id"]}})
            + "\n"
            + json.dumps(data)
            + "\n"
        )

        await self.client.bulk(body, index=index_name)

    async def clear_out(self, fixture: str, index_name: str):
        data = self.read_file(fixture)

        if isinstance(data, dict):
            data = [data]
        elif isinstance(data, list):
            pass
        else:
            data = []

        for item in data:
            await self.client.delete(index_name, item["id"])
