import time

from elasticsearch import Elasticsearch

# TODO: @backoff()
if __name__ == "__main__":
    es_client = Elasticsearch(hosts="http://elastic:9200")
    while True:
        if es_client.ping():
            print("**** Elastic available")
            break
        print("**** Elastic not available")
        time.sleep(10)
