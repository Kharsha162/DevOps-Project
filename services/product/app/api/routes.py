import json
import logging
from flask import Blueprint, jsonify, request
from app.infrastructure.database import Database, ProductRepository
from app.infrastructure.cache import Cache
from app.infrastructure.messaging import MessageBroker
from app.core.use_cases import (
    CreateProductUseCase,
    GetProductUseCase,
    UpdateProductUseCase,
    DeleteProductUseCase,
    ListProductsUseCase
)

logger = logging.getLogger(__name__)
api_bp = Blueprint('product_api', __name__)

_db = Database()
_cache = Cache()
_broker = MessageBroker()
_repository = ProductRepository(_db)

create_product = CreateProductUseCase(_repository, _cache)
get_product = GetProductUseCase(_repository, _cache)
update_product = UpdateProductUseCase(_repository, _cache)
delete_product = DeleteProductUseCase(_repository, _cache)
list_products = ListProductsUseCase(_repository, _cache)


def _error_response(message, status=400):
    return jsonify({"status": "error", "message": message}), status


@api_bp.route('/products', methods=['GET'])
def get_products_route():
    search = request.args.get('search')
    limit = request.args.get('limit', 10)
    offset = request.args.get('offset', 0)

    try:
        products = list_products.execute(search_query=search, limit=limit, offset=offset)
        return jsonify({
            "status": "success",
            "products": products,
            "count": len(products),
            "search": search,
            "limit": int(limit),
            "offset": int(offset)
        })
    except ValueError as err:
        return _error_response(str(err), status=400)
    except Exception as err:
        logger.exception("Failed to list products")
        return _error_response("Unable to read products", status=500)


@api_bp.route('/product/<product_id>', methods=['GET'])
def get_product_route(product_id):
    try:
        product = get_product.execute(product_id)
        if not product:
            return _error_response("Product not found", status=404)
        return jsonify({"status": "success", "product": product})
    except ValueError as err:
        return _error_response(str(err), status=400)
    except Exception as err:
        logger.exception("Failed to get product")
        return _error_response("Unable to read product", status=500)


@api_bp.route('/product', methods=['POST'])
def create_product_route():
    payload = request.get_json(silent=True)
    if not payload:
        return _error_response("Invalid JSON payload", status=400)

    try:
        product = create_product.execute(
            name=payload.get('name'),
            description=payload.get('description', ''),
            price=payload.get('price'),
            stock=payload.get('stock'),
            category=payload.get('category', 'general')
        )
        return jsonify({"status": "success", "product": product}), 201
    except ValueError as err:
        return _error_response(str(err), status=400)
    except Exception as err:
        logger.exception("Failed to create product")
        return _error_response("Unable to create product", status=500)


@api_bp.route('/product/<product_id>', methods=['PUT'])
def update_product_route(product_id):
    payload = request.get_json(silent=True)
    if not payload:
        return _error_response("Invalid JSON payload", status=400)

    try:
        product = update_product.execute(
            product_id=product_id,
            name=payload.get('name'),
            description=payload.get('description'),
            price=payload.get('price'),
            stock=payload.get('stock'),
            category=payload.get('category')
        )
        if not product:
            return _error_response("Product not found", status=404)
        return jsonify({"status": "success", "product": product})
    except ValueError as err:
        return _error_response(str(err), status=400)
    except Exception as err:
        logger.exception("Failed to update product")
        return _error_response("Unable to update product", status=500)


@api_bp.route('/product/<product_id>', methods=['DELETE'])
def delete_product_route(product_id):
    try:
        delete_product.execute(product_id)
        return jsonify({"status": "success", "message": "Product deleted"})
    except ValueError as err:
        return _error_response(str(err), status=404 if "not found" in str(err).lower() else 400)
    except Exception as err:
        logger.exception("Failed to delete product")
        return _error_response("Unable to delete product", status=500)
