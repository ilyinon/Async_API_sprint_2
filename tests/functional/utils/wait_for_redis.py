import time

from redis.client import Redis

from tests.functional.settings import settings

# sys.path.append('/opt/tests/functional')


# TODO: @backoff()
if __name__ == "__main__":
    redis_client = Redis(host=settings.redis_host, port=settings.redis_port, db=0)
    while True:
        if redis_client.ping():
            break
        time.sleep(1)
