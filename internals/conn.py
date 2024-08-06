import redis

redis_conn = None


def get_redis():
    global redis_conn
    if not redis_conn:
        redis_conn = redis.from_url("redis://localhost:6379")
    return redis_conn
