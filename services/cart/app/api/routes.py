import logging
import time

from flask import Blueprint, jsonify, request

logger = logging.getLogger(__name__)

api_bp = Blueprint("cart_api", __name__)

get_cart_uc = None
add_to_cart_uc = None
remove_from_cart_uc = None
db_instance = None
cache_instance = None


def init_routes(get_uc, add_uc, remove_uc, db_inst, cache_inst):
    global get_cart_uc, add_to_cart_uc, remove_from_cart_uc, db_instance, cache_instance
    get_cart_uc = get_uc
    add_to_cart_uc = add_uc
    remove_from_cart_uc = remove_uc
    db_instance = db_inst
    cache_instance = cache_inst


def _resolve_user_id():
    return (
        request.headers.get("X-User-Id")
        or (request.get_json(silent=True) or {}).get("user_id")
        or request.args.get("user_id")
        or "guest"
    )


def _error_response(message, status=400):
    return jsonify({"status": "error", "message": message}), status


@api_bp.route("/health", methods=["GET"])
def health():
    db_healthy = db_instance.check_health()
    cache_healthy = cache_instance.check_health()
    mode = "PRODUCTION"
    if db_instance.use_sqlite or cache_instance.use_in_memory:
        mode = "SANDBOX_MOCK_FALLBACK"

    return jsonify(
        {
            "service": "cart-service",
            "status": "UP",
            "mode": mode,
            "port": 5003,
            "dependencies": {
                "database": "UP" if db_healthy else "DOWN (Fallback to SQLite in-memory active)",
                "cache": "UP" if cache_healthy else "DOWN (Fallback to In-memory Cache active)",
            },
            "timestamp": time.time(),
        }
    ), 200


@api_bp.route("/cart", methods=["GET"])
@api_bp.route("/api/v1/cart", methods=["GET"])
def get_cart():
    user_id = _resolve_user_id()
    try:
        cart_data = get_cart_uc.execute(user_id)
        return jsonify(
            {
                "status": "success",
                "cart": cart_data["items"],
                "total": cart_data["total"],
                "user_id": user_id,
            }
        )
    except ValueError as err:
        logger.warning("Get cart validation error: %s", err)
        return _error_response(str(err), status=400)
    except Exception as err:
        logger.exception("Failed to get cart")
        return _error_response("Unable to retrieve cart", status=500)


@api_bp.route("/cart/add", methods=["POST"])
@api_bp.route("/api/v1/cart/add", methods=["POST"])
def add_to_cart():
    data = request.get_json(silent=True) or {}
    user_id = _resolve_user_id()
    product_id = data.get("product_id")
    name = data.get("name")
    price = data.get("price")
    quantity = data.get("quantity", 1)

    try:
        cart_data = add_to_cart_uc.execute(
            user_id=user_id,
            product_id=product_id,
            name=name,
            price=price,
            quantity=quantity,
        )
        return jsonify(
            {
                "status": "success",
                "message": f"Added {name} to cart",
                "cart": cart_data["items"],
                "total": cart_data["total"],
                "user_id": user_id,
            }
        )
    except ValueError as err:
        logger.warning("Add to cart validation error: %s", err)
        return _error_response(str(err), status=400)
    except Exception as err:
        logger.exception("Failed to add to cart")
        return _error_response("Unable to add item to cart", status=500)


@api_bp.route("/cart/remove", methods=["DELETE"])
@api_bp.route("/api/v1/cart/remove", methods=["DELETE"])
def remove_from_cart():
    data = request.get_json(silent=True) or {}
    user_id = _resolve_user_id()
    product_id = data.get("product_id") or request.args.get("product_id")
    quantity = data.get("quantity") or request.args.get("quantity", type=int)

    try:
        cart_data = remove_from_cart_uc.execute(
            user_id=user_id,
            product_id=product_id,
            quantity=quantity,
        )
        return jsonify(
            {
                "status": "success",
                "message": f"Removed {product_id} from cart",
                "cart": cart_data["items"],
                "total": cart_data["total"],
                "user_id": user_id,
            }
        )
    except ValueError as err:
        logger.warning("Remove from cart validation error: %s", err)
        return _error_response(str(err), status=400)
    except Exception as err:
        logger.exception("Failed to remove from cart")
        return _error_response("Unable to remove item from cart", status=500)
