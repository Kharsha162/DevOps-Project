from flask import Blueprint, jsonify, request

api_bp = Blueprint('notification_api', __name__)

MOCK_HISTORY = [
    {"id": "notif-1", "type": "EMAIL", "recipient": "user@google.com", "body": "Welcome to E-Commerce Platform!"}
]

@api_bp.route('/notifications/send', methods=['POST'])
def send():
    data = request.get_json() or {}
    recipient = data.get('recipient', 'user@example.com')
    body = data.get('body', 'Your order was processed.')
    
    MOCK_HISTORY.append({
        "id": f"notif-{len(MOCK_HISTORY)+1}",
        "type": "EMAIL",
        "recipient": recipient,
        "body": body
    })
    
    return jsonify({
        "status": "success",
        "message": f"Successfully sent notification to {recipient}"
    })

@api_bp.route('/notifications/history', methods=['GET'])
def history():
    return jsonify({
        "status": "success",
        "notifications": MOCK_HISTORY
    })
