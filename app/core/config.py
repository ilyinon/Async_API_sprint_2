import os
from logging import config as logging_config

from core.logger import LOGGING
from pydantic_settings import BaseSettings, SettingsConfigDict

DOTENV = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class EtlSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=DOTENV)

    project_name: str

    elastic_host: str
    elastic_port: int

    redis_host: str
    redis_port: int

    film_cache_expire_in_seconds: int
    genre_cache_expire_in_seconds: int
    person_cache_expire_in_seconds: int

    @property
    def elastic_dsn(self):
        return f"http://{self.elastic_host}:{self.elastic_port}"

    @property
    def redis_dsn(self):
        return f"redis://{self.redis_host}:{self.redis_port}"


settings = EtlSettings()
