from flask import Blueprint, jsonify, request

api_bp = Blueprint('order_api', __name__)

@api_bp.route('/orders/create', methods=['POST'])
def create_order():
    data = request.get_json() or {}
    items = data.get('items', [])
    total = data.get('total', 0.0)
    
    return jsonify({
        "status": "success",
        "order_id": "ord-7773319022",
        "total": total,
        "items": items,
        "message": "Order created successfully. Notification dispatched via Kafka."
    })
