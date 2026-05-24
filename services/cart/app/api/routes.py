from flask import Blueprint, jsonify, request

api_bp = Blueprint('cart_api', __name__)

# Temporary mock persistence in-memory for testing
MOCK_CART = []

@api_bp.route('/cart', methods=['GET'])
def get_cart():
    total = sum(item['price'] * item['quantity'] for item in MOCK_CART)
    return jsonify({
        "status": "success",
        "cart": MOCK_CART,
        "total": total
    })

@api_bp.route('/cart/add', methods=['POST'])
def add_to_cart():
    data = request.get_json() or {}
    prod_id = data.get('product_id', 'prod-1')
    name = data.get('name', 'Product Name')
    price = data.get('price', 10.00)
    qty = data.get('quantity', 1)
    
    # Check if exists
    for item in MOCK_CART:
        if item['product_id'] == prod_id:
            item['quantity'] += qty
            return jsonify({"status": "success", "message": "Increased cart quantity", "cart": MOCK_CART})
            
    MOCK_CART.append({
        "product_id": prod_id,
        "name": name,
        "price": price,
        "quantity": qty
    })
    return jsonify({
        "status": "success",
        "message": f"Added {name} to cart",
        "cart": MOCK_CART
    })
