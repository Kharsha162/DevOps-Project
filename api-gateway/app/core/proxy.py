import logging
import time

import requests
from flask import jsonify, request

from app.config import REQUEST_TIMEOUT, SANDBOX_FALLBACK, SERVICE_ROUTES

logger = logging.getLogger(__name__)


def _match_service(full_path):
    matched = None
    for route_prefix in sorted(SERVICE_ROUTES.keys(), key=len, reverse=True):
        if full_path.startswith(route_prefix):
            matched = route_prefix
            break
    return matched


def _rewrite_path(full_path, route_prefix):
    if route_prefix in ("/api/v1/products", "/api/v1/product"):
        return full_path.replace("/api/v1", "", 1)
    return full_path


def _build_headers():
    headers = {key: value for key, value in request.headers if key.lower() != "host"}
    if hasattr(request, "user_id") and request.user_id:
        headers["X-User-Id"] = request.user_id
    return headers


def _sandbox_response(full_path, error):
    if "auth" in full_path:
        return {
            "status": "success",
            "token": "mock-jwt-token-12345",
            "user": {"id": "mock-123", "username": "guest_user", "role": "buyer"},
            "sandbox_mode": True,
        }
    if "products" in full_path or "product" in full_path:
        return {
            "status": "success",
            "products": [
                {
                    "id": "prod-1",
                    "name": "Resilient Microservices Cloud Book",
                    "price": 49.99,
                    "stock": 12,
                }
            ],
            "sandbox_mode": True,
        }
    if "cart" in full_path:
        return {
            "status": "success",
            "cart": [],
            "total": 0,
            "sandbox_mode": True,
        }
    return {"status": "error", "message": "Downstream unavailable", "details": str(error)}


def proxy_request(record_metrics):
    method = request.method
    full_path = request.path
    route_prefix = _match_service(full_path)

    if not route_prefix:
        return jsonify({"status": "error", "message": "Service route not found"}), 404

    downstream_path = _rewrite_path(full_path, route_prefix)
    target_url = SERVICE_ROUTES[route_prefix]
    url = f"{target_url}{downstream_path}"
    headers = _build_headers()

    start_time = time.time()
    try:
        resp = requests.request(
            method=method,
            url=url,
            headers=headers,
            data=request.get_data(),
            params=request.args,
            timeout=REQUEST_TIMEOUT,
        )
        duration = time.time() - start_time
        record_metrics(method, full_path, resp.status_code, duration)
        logger.info(
            "Proxied %s %s -> %s (%s) in %.3fs",
            method,
            full_path,
            url,
            resp.status_code,
            duration,
        )

        excluded = {
            "content-encoding",
            "content-length",
            "transfer-encoding",
            "connection",
        }
        resp_headers = [
            (name, value)
            for name, value in resp.raw.headers.items()
            if name.lower() not in excluded
        ]
        return resp.content, resp.status_code, resp_headers
    except requests.RequestException as exc:
        duration = time.time() - start_time
        record_metrics(method, full_path, 503, duration)
        logger.error("Proxy failed %s %s -> %s: %s", method, full_path, url, exc)

        if SANDBOX_FALLBACK:
            return jsonify(_sandbox_response(full_path, exc)), 200

        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Downstream service unavailable",
                    "service": route_prefix,
                }
            ),
            503,
        )


def check_downstream_health():
    health_status = {}
    checked = set()

    for route_prefix, service_url in SERVICE_ROUTES.items():
        if service_url in checked:
            continue
        checked.add(service_url)
        service_name = route_prefix.split("/")[-1]
        try:
            res = requests.get(f"{service_url}/health", timeout=REQUEST_TIMEOUT)
            health_status[service_name] = res.json()
        except requests.RequestException:
            health_status[service_name] = {"status": "DOWN"}

    return health_status
