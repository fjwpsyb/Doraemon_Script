import redis
import time
from redis.exceptions import ConnectionError, TimeoutError

def with_retry(retry_count=5, delay=1):
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exception = None
            for _ in range(retry_count):
                try:
                    return func(*args, **kwargs)
                except (ConnectionError, TimeoutError) as e:
                    print(f"Retrying due to error: {e}")
                    last_exception = e
                    time.sleep(delay)
            raise last_exception
        return wrapper
    return decorator

class RedisClient:
    def __init__(self, host='localhost', port=6379, db=0, password=None):
        pool = redis.ConnectionPool(host=host, port=port, db=db, password=password)
        self.client = redis.Redis(connection_pool=pool)

    @with_retry(retry_count=5, delay=1)
    def set(self, key, value):
        self.client.set(key, value)

    @with_retry(retry_count=5, delay=1)
    def get(self, key):
        result = self.client.get(key)
        if result:
            return result
        return None

    @with_retry(retry_count=5, delay=1)
    def delete(self, key):
        self.client.delete(key)
