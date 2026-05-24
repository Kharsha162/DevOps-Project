import os
import time
import requests
from flask import Flask, jsonify, request
from prometheus_client import make_wsgi_app, Counter, Histogram
from werkzeug.middleware.dispatcher import DispatcherMiddleware

REQUEST_COUNT = Counter('gateway_requests_total', 'Total API Gateway Requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('gateway_request_duration_seconds', 'Gateway HTTP Latency', ['method', 'endpoint'])

def create_app():
    app = Flask("api-gateway")

    # Routing mappings from Env or defaults
    ROUTES = {
        "/api/v1/auth": os.getenv("AUTH_SERVICE_URL", "http://127.0.0.1:5001"),
        "/api/v1/products": os.getenv("PRODUCT_SERVICE_URL", "http://127.0.0.1:5002"),
        "/api/v1/cart": os.getenv("CART_SERVICE_URL", "http://127.0.0.1:5003"),
        "/api/v1/orders": os.getenv("ORDER_SERVICE_URL", "http://127.0.0.1:5004"),
        "/api/v1/payments": os.getenv("PAYMENT_SERVICE_URL", "http://127.0.0.1:5005"),
        "/api/v1/notifications": os.getenv("NOTIFICATION_SERVICE_URL", "http://127.0.0.1:5006")
    }

    @app.route('/')
    def index():
        return jsonify({
            "service": "api-gateway",
            "status": "UP",
            "uptime": "Healthy",
            "routes": ROUTES,
            "timestamp": time.time()
        })

    @app.route('/health')
    def health():
        health_status = {}
        for path, url in ROUTES.items():
            try:
                # 1 second timeout to keep it quick
                res = requests.get(f"{url}/health", timeout=1)
                health_status[path.split('/')[-1]] = res.json()
            except Exception:
                health_status[path.split('/')[-1]] = {"status": "DEGRADED (Mock Mode Fallback Enabled)"}

        return jsonify({
            "service": "api-gateway",
            "status": "UP",
            "downstreams": health_status,
            "timestamp": time.time()
        })

    # Catch-all route to reverse-proxy requests
    @app.route('/api/v1/<path:subpath>', methods=['GET', 'POST', 'PUT', 'DELETE'])
    def proxy(subpath):
        method = request.method
        full_path = request.path
        
        # Match base route prefix
        matched_service_url = None
        for route, target_url in ROUTES.items():
            if full_path.startswith(route):
                matched_service_url = target_url
                break
        
        if not matched_service_url:
            return jsonify({"error": "Service route not found"}), 404

        url = f"{matched_service_url}{full_path}"
        headers = {key: value for key, value in request.headers if key != 'Host'}
        
        start_time = time.time()
        try:
            # Proxy request to actual service
            resp = requests.request(
                method=method,
                url=url,
                headers=headers,
                data=request.get_data(),
                params=request.args,
                timeout=2
            )
            
            # Record Prometheus Metrics
            duration = time.time() - start_time
            REQUEST_COUNT.labels(method=method, endpoint=full_path, status=resp.status_code).inc()
            REQUEST_LATENCY.labels(method=method, endpoint=full_path).observe(duration)
            
            # Reconstruct response
            excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
            resp_headers = [(name, value) for name, value in resp.raw.headers.items() if name.lower() not in excluded_headers]
            return resp.content, resp.status_code, resp_headers
            
        except Exception as e:
            # Resilient Fallback Simulator (Returns clean mocks if service is down)
            duration = time.time() - start_time
            REQUEST_COUNT.labels(method=method, endpoint=full_path, status=503).inc()
            
            # Fallback mocks per service path
            if "auth" in full_path:
                mock_res = {"user": {"id": "mock-123", "username": "guest_user", "role": "buyer"}, "token": "mock-jwt-token-12345", "sandbox_mode": True}
            elif "products" in full_path:
                mock_res = {
                    "products": [
                        {"id": "prod-1", "name": "Resilient Microservices Cloud Book", "price": 49.99, "stock": 12},
                        {"id": "prod-2", "name": "Vibrant CSS Glassmorphism Mug", "price": 19.99, "stock": 85},
                        {"id": "prod-3", "name": "Kubernetes Pod Pilot Leather Jacket", "price": 129.99, "stock": 5}
                    ],
                    "sandbox_mode": True
                }
            elif "cart" in full_path:
                mock_res = {"items": [{"product_id": "prod-2", "quantity": 2, "name": "Vibrant CSS Glassmorphism Mug", "price": 19.99}], "total": 39.98, "sandbox_mode": True}
            elif "orders" in full_path:
                mock_res = {"order_id": "ord-mock-9876", "status": "PENDING (Gateway Fallback)", "total": 39.98, "sandbox_mode": True}
            elif "payments" in full_path:
                mock_res = {"transaction_id": "tx-mock-5555", "status": "SUCCESS (Gateway Mock)", "sandbox_mode": True}
            elif "notifications" in full_path:
                mock_res = {"message": "Notification event queued successfully", "sandbox_mode": True}
            else:
                mock_res = {"error": "Downstream service unavailable and no mock exists", "details": str(e)}
                
            return jsonify(mock_res), 200

    # Add Prometheus metrics
    app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
        '/metrics': make_wsgi_app()
    })

    return app
