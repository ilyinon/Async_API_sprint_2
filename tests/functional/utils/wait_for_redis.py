import time

from redis.client import Redis

# TODO: @backoff()
if __name__ == "__main__":
    redis_client = Redis.from_url("redis://redis:6379")
    while True:
        if redis_client.ping():
            print("**** Reddis available")
            break
        print("**** Reddis not available")
        time.sleep(10)
