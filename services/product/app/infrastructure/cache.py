import os
import json
import logging
import redis

logger = logging.getLogger(__name__)

class Cache:
    def __init__(self):
        self.redis_host = os.getenv("REDIS_HOST", "localhost")
        self.redis_port = int(os.getenv("REDIS_PORT", 6379))
        self.client = redis.Redis(
            host=self.redis_host,
            port=self.redis_port,
            db=0,
            socket_connect_timeout=1,
            socket_timeout=1,
            decode_responses=True
        )

    def check_health(self):
        try:
            return self.client.ping()
        except Exception as exc:
            logger.warning("Redis health check failed: %s", exc)
            return False

    def get_product(self, key):
        try:
            payload = self.client.get(key)
            if not payload:
                return None
            return json.loads(payload)
        except Exception as exc:
            logger.warning("Redis get_product failed for %s: %s", key, exc)
            return None

    def set_product(self, key, value, ttl=600):
        try:
            self.client.set(key, json.dumps(value), ex=ttl)
        except Exception as exc:
            logger.warning("Redis set_product failed for %s: %s", key, exc)

    def get_list(self, key):
        try:
            payload = self.client.get(key)
            if not payload:
                return None
            return json.loads(payload)
        except Exception as exc:
            logger.warning("Redis get_list failed for %s: %s", key, exc)
            return None

    def set_list(self, key, value, ttl=300):
        try:
            self.client.set(key, json.dumps(value), ex=ttl)
        except Exception as exc:
            logger.warning("Redis set_list failed for %s: %s", key, exc)

    def delete(self, key_pattern):
        try:
            if '*' in key_pattern:
                keys = self.client.keys(key_pattern)
                if keys:
                    self.client.delete(*keys)
            else:
                self.client.delete(key_pattern)
        except Exception as exc:
            logger.warning("Redis delete failed for %s: %s", key_pattern, exc)
