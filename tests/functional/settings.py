import os

from pydantic_settings import BaseSettings, SettingsConfigDict

DOTENV = os.path.abspath(os.path.join(os.path.dirname(__file__), "../..", ".env_test"))


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=DOTENV)

    project_name: str

    elastic_host: str
    elastic_port: int

    redis_host: str
    redis_port: int

    app_host: str = "app_test"
    app_port: int = 7000

    film_cache_expire_in_seconds: int
    genre_cache_expire_in_seconds: int
    person_cache_expire_in_seconds: int

    movies_index: str = "movies_test"
    genres_index: str = "genres_test"
    persons_index: str = "persons_test"

    SIZE: int = 26

    @property
    def elastic_dsn(self):
        return f"http://{self.elastic_host}:{self.elastic_port}"

    @property
    def redis_dsn(self):
        return f"redis://{self.redis_host}:{self.redis_port}"

    @property
    def app_dsn(self):
        return f"http://{self.app_host}:{self.app_port}"


settings = TestSettings()
