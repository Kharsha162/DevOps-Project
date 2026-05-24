import os
import time
import logging
from flask import Flask, jsonify, request
from prometheus_client import make_wsgi_app, Counter, Histogram
from werkzeug.middleware.dispatcher import DispatcherMiddleware

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)
logger = logging.getLogger("product-service")

# Core Prometheus metrics
REQUEST_COUNT = Counter('product_requests_total', 'Total HTTP Requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('product_request_duration_seconds', 'HTTP Request Duration', ['method', 'endpoint'])


def create_app():
    app = Flask("product-service")
    app.logger = logger
    app.logger.setLevel(logging.INFO)

    from app.infrastructure.database import Database
    from app.infrastructure.cache import Cache
    from app.infrastructure.messaging import MessageBroker

    db = Database()
    cache = Cache()
    broker = MessageBroker()

    @app.route('/')
    def index():
        return jsonify({
            "service": "product-service",
            "status": "UP",
            "port": int(os.getenv("PORT", 5002)),
            "timestamp": time.time()
        })

    @app.route('/health')
    def health():
        db_healthy = db.check_health()
        redis_healthy = cache.check_health()
        kafka_required = os.getenv("KAFKA_BOOTSTRAP_SERVERS") is not None
        kafka_healthy = broker.check_health() if kafka_required else None

        dependencies = {
            "database": "UP" if db_healthy else "DOWN",
            "cache": "UP" if redis_healthy else "DOWN"
        }
        if kafka_required:
            dependencies["kafka"] = "UP" if kafka_healthy else "DOWN"

        return jsonify({
            "service": "product-service",
            "status": "UP" if db_healthy and redis_healthy else "DEGRADED",
            "port": int(os.getenv("PORT", 5002)),
            "dependencies": dependencies,
            "timestamp": time.time()
        })

    @app.before_request
    def before_request():
        app.start_time = time.time()

    @app.after_request
    def after_request(response):
        if hasattr(app, 'start_time'):
            duration = time.time() - app.start_time
            REQUEST_COUNT.labels(method=request.method, endpoint=request.path, status=response.status_code).inc()
            REQUEST_LATENCY.labels(method=request.method, endpoint=request.path).observe(duration)
        return response

    # Mount Prometheus /metrics endpoint
    app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
        '/metrics': make_wsgi_app()
    })

    from app.api.routes import api_bp
    app.register_blueprint(api_bp, url_prefix='')

    return app
