from redis.client import Redis
from settings import settings
from utils.backoff import backoff
from utils.logger import logger


@backoff()
def wait_for_redis():
    redis_client = Redis(host=settings.redis_host, port=settings.redis_port, db=0)
    ping = redis_client.ping()
    logger.info(ping)
    if ping:
        return ping
    raise Exception


if __name__ == "__main__":
    wait_for_redis()
