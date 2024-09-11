import time

from redis.client import Redis

# TODO: @backoff()
if __name__ == "__main__":
    redis_client = Redis(
        hosts="http://localhost:6379", validate_cert=False, use_ssl=False
    )
    while True:
        if redis_client.ping():
            break
        time.sleep(1)
