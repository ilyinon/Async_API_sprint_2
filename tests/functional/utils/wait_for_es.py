import sys
import time

from elasticsearch import Elasticsearch

from tests.functional.settings import settings

sys.path.append("/opt/tests")


# TODO: @backoff()
if __name__ == "__main__":
    es_client = Elasticsearch(hosts=settings.elastic_dsn)
    while True:
        if es_client.ping():
            break
        time.sleep(1)
