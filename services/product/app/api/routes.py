from flask import Blueprint, jsonify
from app.infrastructure.database import Database
from app.infrastructure.cache import Cache
from app.infrastructure.messaging import MessageBroker
from app.core.use_cases import ProductUseCases

api_bp = Blueprint('product_api', __name__)

db = Database()
cache = Cache()
broker = MessageBroker()
use_cases = ProductUseCases(db, cache, broker)

@api_bp.route('/products', methods=['GET'])
def get_products():
    # Return mock lists for beautiful interactive UI
    products = [
        {"id": "prod-1", "name": "Resilient Microservices Cloud Book", "price": 49.99, "stock": 12},
        {"id": "prod-2", "name": "Vibrant CSS Glassmorphism Mug", "price": 19.99, "stock": 85},
        {"id": "prod-3", "name": "Kubernetes Pod Pilot Leather Jacket", "price": 129.99, "stock": 5}
    ]
    return jsonify({
        "status": "success",
        "products": products,
        "total": len(products)
    })
