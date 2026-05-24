import os
import time
from flask import Flask, jsonify, request
from prometheus_client import make_wsgi_app, Counter, Histogram
from werkzeug.middleware.dispatcher import DispatcherMiddleware

# Core Prometheus metrics
REQUEST_COUNT = Counter('product_requests_total', 'Total HTTP Requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('product_request_duration_seconds', 'HTTP Request Duration', ['method', 'endpoint'])

def create_app():
    app = Flask("product-service")

    # Clean Domain dependencies initialized
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
            "port": 5002,
            "timestamp": time.time()
        })

    @app.route('/health')
    def health():
        db_healthy = db.check_health()
        redis_healthy = cache.check_health()
        kafka_healthy = broker.check_health()
        
        return jsonify({
            "service": "product-service",
            "status": "UP",
            "port": 5002,
            "dependencies": {
                "database": "UP" if db_healthy else "DOWN (Graceful Sandbox Fallback)",
                "cache": "UP" if redis_healthy else "DOWN (Graceful Sandbox Fallback)",
                "kafka": "UP" if kafka_healthy else "DOWN (Graceful Sandbox Fallback)"
            },
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

    # Register API blueprint
    from app.api.routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api/v1')

    return app
