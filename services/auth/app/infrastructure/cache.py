import os
import redis
import logging
import threading
import time

logger = logging.getLogger(__name__)

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
                # Fast socket connection check first (0.2s timeout)
                import socket
                s = socket.create_connection((self.redis_host, self.redis_port), timeout=0.2)
                s.close()
                
                # Initialize Redis client
                self._client = redis.Redis(
                    host=self.redis_host,
                    port=self.redis_port,
                    socket_timeout=0.5,
                    socket_connect_timeout=0.5
                )
                self._client.ping()
                logger.info("Redis Session Cache initialized successfully.")
            except Exception as e:
                logger.warning(f"Redis connection failed ({e}). Falling back to Sandbox Mode (In-memory Cache)...")
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


class SessionCache:
    def __init__(self, cache_instance):
        self.cache = cache_instance

    def set_session(self, user_id, token, ttl=7200):
        # Trigger initialization
        self.cache.get_client()
        if self.cache.use_in_memory:
            with self.cache._lock:
                self.cache._in_memory_store[f"session:{user_id}"] = {
                    "token": token,
                    "expires_at": int(time.time()) + ttl
                }
            return True
        else:
            try:
                self.cache._client.setex(f"session:{user_id}", ttl, token)
                return True
            except Exception as e:
                logger.error(f"Failed to write session to Redis: {e}")
                return False

    def get_session(self, user_id):
        # Trigger initialization
        self.cache.get_client()
        if self.cache.use_in_memory:
            with self.cache._lock:
                session = self.cache._in_memory_store.get(f"session:{user_id}")
                if session:
                    # Optional expiry check
                    if session["expires_at"] > int(time.time()):
                        return session["token"]
            return None
        else:
            try:
                token = self.cache._client.get(f"session:{user_id}")
                return token.decode("utf-8") if token else None
            except Exception as e:
                logger.error(f"Failed to fetch session from Redis: {e}")
                return None
