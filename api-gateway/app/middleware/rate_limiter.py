import logging
import threading
import time
from collections import defaultdict, deque

from flask import jsonify, request

from app.config import RATE_LIMIT_PER_MINUTE

logger = logging.getLogger(__name__)


class RateLimiter:
    def __init__(self, limit_per_minute):
        self.limit = limit_per_minute
        self._requests = defaultdict(deque)
        self._lock = threading.Lock()

    def _client_key(self):
        forwarded = request.headers.get("X-Forwarded-For", "")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.remote_addr or "unknown"

    def check(self):
        if request.path in {"/", "/health", "/metrics"}:
            return None

        now = time.time()
        key = self._client_key()

        with self._lock:
            window = self._requests[key]
            while window and window[0] <= now - 60:
                window.popleft()

            if len(window) >= self.limit:
                logger.warning("Rate limit exceeded for %s on %s", key, request.path)
                return (
                    jsonify(
                        {
                            "status": "error",
                            "message": "Rate limit exceeded. Try again later.",
                        }
                    ),
                    429,
                )

            window.append(now)

        return None
