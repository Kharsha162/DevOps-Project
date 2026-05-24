from flask import Blueprint, jsonify, request

api_bp = Blueprint('payment_api', __name__)

@api_bp.route('/payments/process', methods=['POST'])
def process():
    data = request.get_json() or {}
    order_id = data.get('order_id', 'ord-123')
    amount = data.get('amount', 0.00)
    
    return jsonify({
        "status": "success",
        "transaction_id": "tx-stripe-883391",
        "amount": amount,
        "order_id": order_id,
        "gateway": "stripe-mock-processor"
    })
