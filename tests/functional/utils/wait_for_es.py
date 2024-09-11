import time

from elasticsearch import Elasticsearch

# TODO: @backoff()

if __name__ == "__main__":
    es_client = Elasticsearch(
        hosts="http://localhost:9200"
    )
    while True:
        if es_client.ping():
            break
        time.sleep(1)
