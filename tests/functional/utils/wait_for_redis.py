from redis.client import Redis
from functional.settings import settings
from functional.utils.backoff import backoff
from functional.utils.logger import logger


@backoff()
def wait_for_redis():
    redis_client = Redis(host=settings.redis_host, port=settings.redis_port, db=0)
    ping = redis_client.ping()

    if ping:
        return ping
    logger.info(f"redis ping: {ping}")


if __name__ == "__main__":

    wait_for_redis()
