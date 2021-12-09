from pydantic import BaseSettings


class ESSettings(BaseSettings):
    HOST: str = "127.0.0.1"
    PORT: str = "9200"

    class Config:
        env_prefix = "ELASTIC_"

    @property
    def get_dsl(self):
        return f"{self.HOST}:{self.PORT}"


class RedisSettings(BaseSettings):
    HOST: str = "127.0.0.1"
    PORT: str = "6379"
    TTL: int = 10

    class Config:
        env_prefix = "REDIS_"


class CommonSettings(BaseSettings):
    PROJECT_NAME: str = "movies_tests"

    SERVICE_URL: str = "http://127.0.0.1:8000"

    DEFAULT_PAGE_NUMBER: int = 1
    DEFAULT_PAGE_SIZE: int = 50

    ES: ESSettings = ESSettings()
    Redis: RedisSettings = RedisSettings()


settings = CommonSettings()
