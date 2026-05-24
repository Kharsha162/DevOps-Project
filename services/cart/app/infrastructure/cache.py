import os
import socket

class Cache:
    def __init__(self):
        self.redis_host = os.getenv("REDIS_HOST", "localhost")
        self.redis_port = int(os.getenv("REDIS_PORT", 6379))

    def check_health(self):
        try:
            # Non-blocking TCP socket check
            s = socket.create_connection((self.redis_host, self.redis_port), timeout=0.5)
            s.close()
            return True
        except Exception:
            return False
