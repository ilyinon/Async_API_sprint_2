from elasticsearch import Elasticsearch
from settings import settings
from utils.backoff import backoff
from utils.logger import logger


@backoff()
def wait_for_es():
    es_client = Elasticsearch(hosts=settings.elastic_dsn)
    ping = es_client.ping()
    logger.info(ping)
    if ping:
        return ping
    raise Exception


if __name__ == "__main__":

    wait_for_es()
