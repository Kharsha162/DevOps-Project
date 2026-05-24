import os
import socket
from urllib.parse import urlparse

class Database:
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/ecommerce")

    def check_health(self):
        try:
            # Non-blocking TCP socket check to prevent crashing/blocking if DB is not ready
            parsed = urlparse(self.db_url)
            host = parsed.hostname or 'localhost'
            port = parsed.port or 5432
            s = socket.create_connection((host, port), timeout=0.5)
            s.close()
            return True
        except Exception:
            return False
