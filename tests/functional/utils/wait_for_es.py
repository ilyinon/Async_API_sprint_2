from elasticsearch import ConnectionError, Elasticsearch
from functional.settings import settings
from functional.utils.backoff import backoff
from functional.utils.logger import logger


@backoff()
def wait_for_es():
    es_client = Elasticsearch(hosts=settings.elastic_dsn)
    ping = es_client.ping()
    if not ping:
        raise ConnectionError
    logger.info(f"elastic ping: {ping}")


if __name__ == "__main__":

    wait_for_es()
