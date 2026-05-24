import os
import time
import logging
from flask import Flask, jsonify, request
from prometheus_client import make_wsgi_app, Counter, Histogram
from werkzeug.middleware.dispatcher import DispatcherMiddleware

# Configure logging beautifully
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter('auth_requests_total', 'Total HTTP Requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('auth_request_duration_seconds', 'HTTP Request Duration', ['method', 'endpoint'])

def create_app():
    app = Flask("auth-service")

    # 1. Initialize Infrastructure Components
    from app.infrastructure.database import Database, UserRepository
    from app.infrastructure.cache import Cache, SessionCache

    db = Database()
    user_repo = UserRepository(db)

    cache = Cache()
    session_cache = SessionCache(cache)

    # 2. Initialize Use Cases (Clean Architecture Dependency Injection)
    from app.core.use_cases import RegisterUseCase, LoginUseCase
    register_uc = RegisterUseCase(user_repo)
    login_uc = LoginUseCase(user_repo, session_cache)

    # 3. Initialize REST Routes Blueprint
    from app.api.routes import api_bp, init_routes
    init_routes(register_uc, login_uc, db, cache)
    app.register_blueprint(api_bp)

    # Base Index route
    @app.route('/')
    def index():
        mode = "SANDBOX_MOCK_FALLBACK" if (db.use_sqlite or cache.use_in_memory) else "PRODUCTION"
        return jsonify({
            "service": "auth-service",
            "status": "UP",
            "mode": mode,
            "port": 5001,
            "timestamp": time.time()
        }), 200

    # 4. Metrics Recording Hooks
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

    # 5. Mount Prometheus WSGI endpoint
    app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
        '/metrics': make_wsgi_app()
    })

    return app
