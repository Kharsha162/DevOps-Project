import os
import time
import logging

from flask import Flask, jsonify, request
from prometheus_client import Counter, Histogram, make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

REQUEST_COUNT = Counter(
    "cart_requests_total", "Total HTTP Requests", ["method", "endpoint", "status"]
)
REQUEST_LATENCY = Histogram(
    "cart_request_duration_seconds", "HTTP Request Duration", ["method", "endpoint"]
)


def create_app():
    app = Flask("cart-service")

    from app.infrastructure.database import Database, CartRepository
    from app.infrastructure.cache import Cache, CartCache
    from app.infrastructure.messaging import MessageBroker
    from app.core.use_cases import (
        GetCartUseCase,
        AddToCartUseCase,
        RemoveFromCartUseCase,
    )
    from app.api.routes import api_bp, init_routes

    db = Database()
    cart_repo = CartRepository(db)
    cache = Cache()
    cart_cache = CartCache(cache)
    broker = MessageBroker()

    get_cart_uc = GetCartUseCase(cart_repo, cart_cache)
    add_to_cart_uc = AddToCartUseCase(cart_repo, cart_cache, broker)
    remove_from_cart_uc = RemoveFromCartUseCase(cart_repo, cart_cache, broker)

    init_routes(get_cart_uc, add_to_cart_uc, remove_from_cart_uc, db, cache)
    app.register_blueprint(api_bp)

    @app.route("/")
    def index():
        mode = (
            "SANDBOX_MOCK_FALLBACK"
            if (db.use_sqlite or cache.use_in_memory)
            else "PRODUCTION"
        )
        return jsonify(
            {
                "service": "cart-service",
                "status": "UP",
                "mode": mode,
                "port": int(os.getenv("PORT", 5003)),
                "timestamp": time.time(),
            }
        )

    @app.route("/health")
    def health():
        db_healthy = db.check_health()
        redis_healthy = cache.check_health()
        mode = (
            "SANDBOX_MOCK_FALLBACK"
            if (db.use_sqlite or cache.use_in_memory)
            else "PRODUCTION"
        )

        return jsonify(
            {
                "service": "cart-service",
                "status": "UP",
                "mode": mode,
                "port": int(os.getenv("PORT", 5003)),
                "dependencies": {
                    "database": "UP" if db_healthy else "DOWN (Fallback to SQLite in-memory active)",
                    "cache": "UP" if redis_healthy else "DOWN (Fallback to In-memory Cache active)",
                },
                "timestamp": time.time(),
            }
        )

    @app.before_request
    def before_request():
        app.start_time = time.time()

    @app.after_request
    def after_request(response):
        if hasattr(app, "start_time"):
            duration = time.time() - app.start_time
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=request.path,
                status=response.status_code,
            ).inc()
            REQUEST_LATENCY.labels(
                method=request.method, endpoint=request.path
            ).observe(duration)
        return response

    app.wsgi_app = DispatcherMiddleware(
        app.wsgi_app, {"/metrics": make_wsgi_app()}
    )

    return app
