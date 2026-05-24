import os

JWT_SECRET = os.getenv("JWT_SECRET", "super-secret-key-998877")
JWT_ALGORITHM = "HS256"

RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
REQUEST_TIMEOUT = float(os.getenv("GATEWAY_REQUEST_TIMEOUT", "5"))
SANDBOX_FALLBACK = os.getenv("GATEWAY_SANDBOX_FALLBACK", "false").lower() == "true"

SERVICE_ROUTES = {
    "/api/v1/auth": os.getenv("AUTH_SERVICE_URL", "http://127.0.0.1:5001"),
    "/api/v1/products": os.getenv("PRODUCT_SERVICE_URL", "http://127.0.0.1:5002"),
    "/api/v1/product": os.getenv("PRODUCT_SERVICE_URL", "http://127.0.0.1:5002"),
    "/api/v1/cart": os.getenv("CART_SERVICE_URL", "http://127.0.0.1:5003"),
    "/api/v1/orders": os.getenv("ORDER_SERVICE_URL", "http://127.0.0.1:5004"),
    "/api/v1/payments": os.getenv("PAYMENT_SERVICE_URL", "http://127.0.0.1:5005"),
    "/api/v1/notifications": os.getenv(
        "NOTIFICATION_SERVICE_URL", "http://127.0.0.1:5006"
    ),
}

PUBLIC_PATHS = {
    "/",
    "/health",
    "/metrics",
    "/api/v1/auth/register",
    "/api/v1/auth/login",
    "/signup",
    "/login",
}

PUBLIC_GET_PREFIXES = (
    "/api/v1/products",
    "/api/v1/product/",
)
