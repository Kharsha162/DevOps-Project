from flask import Blueprint, jsonify, request
import logging
import time

logger = logging.getLogger(__name__)

api_bp = Blueprint('auth_api', __name__)

# To be set via dependency injection during create_app()
register_use_case = None
login_use_case = None
db_instance = None
cache_instance = None

def init_routes(reg_uc, log_uc, db_inst, cache_inst):
    global register_use_case, login_use_case, db_instance, cache_instance
    register_use_case = reg_uc
    login_use_case = log_uc
    db_instance = db_inst
    cache_instance = cache_inst

@api_bp.route('/health', methods=['GET'])
def health():
    db_healthy = db_instance.check_health()
    cache_healthy = cache_instance.check_health()
    
    # Active mode
    mode = "PRODUCTION"
    if db_instance.use_sqlite or cache_instance.use_in_memory:
        mode = "SANDBOX_MOCK_FALLBACK"

    return jsonify({
        "service": "auth-service",
        "status": "UP",
        "mode": mode,
        "dependencies": {
            "database": "UP" if db_healthy else "DOWN (Fallback to SQLite in-memory active)",
            "cache": "UP" if cache_healthy else "DOWN (Fallback to In-memory Cache active)"
        },
        "timestamp": time.time()
    }), 200

@api_bp.route('/signup', methods=['POST'])
@api_bp.route('/api/v1/auth/register', methods=['POST'])
def signup():
    data = request.get_json() or {}
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'user')

    if not username or not email or not password:
        logger.warning("Signup failed: Missing required fields")
        return jsonify({
            "status": "error",
            "message": "Missing required fields: username, email, password"
        }), 400

    try:
        user_data = register_use_case.execute(username, email, password)
        logger.info(f"Successfully registered user: {username}")
        return jsonify({
            "status": "success",
            "message": "User registered successfully",
            "user": user_data
        }), 201
    except ValueError as e:
        logger.warning(f"Signup validation error: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400
    except Exception as e:
        logger.error(f"Internal signup error: {e}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": "An internal server error occurred"
        }), 500

@api_bp.route('/login', methods=['POST'])
@api_bp.route('/api/v1/auth/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    # Accept both email/username payloads
    username_or_email = data.get('username') or data.get('email')
    password = data.get('password')

    if not username_or_email or not password:
        logger.warning("Login failed: Missing required fields")
        return jsonify({
            "status": "error",
            "message": "Missing required fields: username/email and password"
        }), 400

    try:
        result = login_use_case.execute(username_or_email, password)
        logger.info(f"User logged in successfully: {username_or_email}")
        return jsonify({
            "status": "success",
            "message": "Login successful",
            "token": result["token"],
            "expires_at": result["expires_at"],
            "user": result["user"]
        }), 200
    except ValueError as e:
        msg = str(e)
        status_code = 401 if "Invalid" in msg or "Credentials" in msg else 400
        logger.warning(f"Login authentication error: {msg}")
        return jsonify({
            "status": "error",
            "message": msg
        }), status_code
    except Exception as e:
        logger.error(f"Internal login error: {e}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": "An internal server error occurred"
        }), 500
