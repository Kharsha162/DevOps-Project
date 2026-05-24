import logging

import jwt
from flask import jsonify, request

from app.config import JWT_ALGORITHM, JWT_SECRET, PUBLIC_GET_PREFIXES, PUBLIC_PATHS

logger = logging.getLogger(__name__)


def _is_public_request():
    path = request.path
    if path in PUBLIC_PATHS:
        return True
    if request.method == "GET" and path.startswith(PUBLIC_GET_PREFIXES):
        return True
    return False


def verify_jwt():
    if _is_public_request():
        return None

    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        logger.warning("Missing or invalid Authorization header for %s", request.path)
        return jsonify({"status": "error", "message": "Authorization token required"}), 401

    token = auth_header.split(" ", 1)[1].strip()
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        request.user_id = payload.get("sub")
        request.user_role = payload.get("role")
        request.jwt_payload = payload
        return None
    except jwt.ExpiredSignatureError:
        logger.warning("Expired JWT for %s", request.path)
        return jsonify({"status": "error", "message": "Token expired"}), 401
    except jwt.InvalidTokenError as exc:
        logger.warning("Invalid JWT for %s: %s", request.path, exc)
        return jsonify({"status": "error", "message": "Invalid token"}), 401
