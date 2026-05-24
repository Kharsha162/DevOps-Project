import logging
import time

from flask import Flask, jsonify, request
from prometheus_client import Counter, Histogram, make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware

from app.config import RATE_LIMIT_PER_MINUTE, SERVICE_ROUTES
from app.core.proxy import check_downstream_health, proxy_request
from app.middleware.jwt_auth import verify_jwt
from app.middleware.rate_limiter import RateLimiter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

REQUEST_COUNT = Counter(
    "gateway_requests_total",
    "Total API Gateway Requests",
    ["method", "endpoint", "status"],
)
REQUEST_LATENCY = Histogram(
    "gateway_request_duration_seconds",
    "Gateway HTTP Latency",
    ["method", "endpoint"],
)


def create_app():
    app = Flask("api-gateway")
    rate_limiter = RateLimiter(limit_per_minute=RATE_LIMIT_PER_MINUTE)

    def record_metrics(method, endpoint, status, duration):
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status).inc()
        REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(duration)

    @app.route("/")
    def index():
        return jsonify(
            {
                "service": "api-gateway",
                "status": "UP",
                "routes": SERVICE_ROUTES,
                "features": ["jwt-auth", "rate-limiting", "reverse-proxy"],
                "timestamp": time.time(),
            }
        )

    @app.route("/health")
    def health():
        downstream = check_downstream_health()
        all_up = all(
            info.get("status") in ("UP", "success")
            or info.get("service")
            for info in downstream.values()
        )
        return jsonify(
            {
                "service": "api-gateway",
                "status": "UP" if all_up else "DEGRADED",
                "downstreams": downstream,
                "timestamp": time.time(),
            }
        )

    @app.before_request
    def before_request():
        app.start_time = time.time()
        rate_response = rate_limiter.check()
        if rate_response:
            return rate_response
        jwt_response = verify_jwt()
        if jwt_response:
            return jwt_response

    @app.route("/api/v1/<path:subpath>", methods=["GET", "POST", "PUT", "DELETE"])
    def proxy(subpath):
        return proxy_request(record_metrics)

    app.wsgi_app = DispatcherMiddleware(
        app.wsgi_app, {"/metrics": make_wsgi_app()}
    )

    return app
