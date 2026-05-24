# API Gateway

Central reverse proxy for the e-commerce microservices platform.

**Port:** `5000`

## Features

- Reverse proxy routing to Auth, Product, Cart, Order, Payment, Notification services
- JWT authentication middleware (protects write/cart routes)
- Rate limiting (60 requests/minute per client IP)
- Structured logging
- Prometheus metrics at `/metrics`
- Downstream health aggregation at `/health`

## Routes

| Gateway Path | Downstream Service |
|---|---|
| `/api/v1/auth/*` | Auth Service (5001) |
| `/api/v1/products`, `/api/v1/product/*` | Product Service (5002) |
| `/api/v1/cart/*` | Cart Service (5003) |
| `/api/v1/orders/*` | Order Service (5004) |
| `/api/v1/payments/*` | Payment Service (5005) |
| `/api/v1/notifications/*` | Notification Service (5006) |

Product paths are rewritten: `/api/v1/products` → `/products` on the Product Service.

## Public Endpoints (no JWT)

- `GET /health`
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/products`
- `GET /api/v1/product/<id>`

## Protected Endpoints (JWT required)

- All cart routes
- Product create/update/delete
- Order, payment, notification routes

## Environment Variables

| Variable | Default |
|---|---|
| `JWT_SECRET` | `super-secret-key-998877` |
| `RATE_LIMIT_PER_MINUTE` | `60` |
| `GATEWAY_REQUEST_TIMEOUT` | `5` |
| `GATEWAY_SANDBOX_FALLBACK` | `false` |
| `AUTH_SERVICE_URL` | `http://127.0.0.1:5001` |
| `PRODUCT_SERVICE_URL` | `http://127.0.0.1:5002` |
| `CART_SERVICE_URL` | `http://127.0.0.1:5003` |

## Run Locally

```bash
cd api-gateway
pip install -r requirements.txt
python run.py
```

## Example Requests

```bash
# Register
curl -X POST http://localhost:5000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","email":"demo@test.com","password":"secret123"}'

# Login
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"secret123"}'

# List products (public)
curl http://localhost:5000/api/v1/products

# Add to cart (JWT required)
curl -X POST http://localhost:5000/api/v1/cart/add \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"product_id":"p1","name":"Widget","price":9.99,"quantity":1}'
```
