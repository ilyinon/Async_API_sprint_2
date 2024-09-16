from pydantic import Field
from pydantic_settings import BaseSettings

from testdata import es_mapping


class TestSettings(BaseSettings):
    es_host: str = Field('http://elastic:9200')
    es_index: str
    # es_id_field: str
    es_index_mapping: dict

    redis_host: str = Field('redis://redis:6379')
    service_url: str = Field('http://nginx:80')


film_test_settings = TestSettings(es_index="movies_test", es_index_mapping=es_mapping.MAPPING_MOVIES)
person_test_settings = TestSettings(es_index="persons_test", es_index_mapping=es_mapping.MAPPING_PERSONS)
genre_test_settings = TestSettings(es_index="genres_test", es_index_mapping=es_mapping.MAPPING_GENRES)