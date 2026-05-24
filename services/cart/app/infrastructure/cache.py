import os
import json
import logging
import threading
import time

import redis

logger = logging.getLogger(__name__)

CART_CACHE_TTL = 86400


class Cache:
    def __init__(self):
        self.redis_host = os.getenv("REDIS_HOST", "127.0.0.1")
        self.redis_port = int(os.getenv("REDIS_PORT", 6379))
        self.use_in_memory = False
        self._in_memory_store = {}
        self._lock = threading.Lock()
        self._client = None
        self._initialized = False

    def _initialize_cache(self):
        with self._lock:
            if self._initialized:
                return
            try:
                import socket

                s = socket.create_connection(
                    (self.redis_host, self.redis_port), timeout=0.2
                )
                s.close()

                self._client = redis.Redis(
                    host=self.redis_host,
                    port=self.redis_port,
                    db=0,
                    socket_timeout=0.5,
                    socket_connect_timeout=0.5,
                    decode_responses=True,
                )
                self._client.ping()
                logger.info("Redis cart cache initialized successfully.")
            except Exception as exc:
                logger.warning(
                    "Redis connection failed (%s). Falling back to in-memory cache.",
                    exc,
                )
                self.use_in_memory = True
            self._initialized = True

    def get_client(self):
        self._initialize_cache()
        return self._client

    def check_health(self):
        self._initialize_cache()
        if self.use_in_memory:
            return False
        try:
            return self._client.ping()
        except Exception:
            return False


class CartCache:
    def __init__(self, cache_instance):
        self.cache = cache_instance

    def _cart_key(self, user_id):
        return f"cart:{user_id}"

    def get_cart(self, user_id):
        self.cache.get_client()
        key = self._cart_key(user_id)

        if self.cache.use_in_memory:
            with self.cache._lock:
                entry = self.cache._in_memory_store.get(key)
                if entry and entry["expires_at"] > int(time.time()):
                    return entry["payload"]
            return None

        try:
            payload = self.cache._client.get(key)
            if not payload:
                return None
            return json.loads(payload)
        except Exception as exc:
            logger.warning("Redis get_cart failed for %s: %s", user_id, exc)
            return None

    def set_cart(self, user_id, cart_data, ttl=CART_CACHE_TTL):
        self.cache.get_client()
        key = self._cart_key(user_id)

        if self.cache.use_in_memory:
            with self.cache._lock:
                self.cache._in_memory_store[key] = {
                    "payload": cart_data,
                    "expires_at": int(time.time()) + ttl,
                }
            return True

        try:
            self.cache._client.set(key, json.dumps(cart_data), ex=ttl)
            return True
        except Exception as exc:
            logger.warning("Redis set_cart failed for %s: %s", user_id, exc)
            return False

    def delete_cart(self, user_id):
        self.cache.get_client()
        key = self._cart_key(user_id)

        if self.cache.use_in_memory:
            with self.cache._lock:
                self.cache._in_memory_store.pop(key, None)
            return True

        try:
            self.cache._client.delete(key)
            return True
        except Exception as exc:
            logger.warning("Redis delete_cart failed for %s: %s", user_id, exc)
            return False
