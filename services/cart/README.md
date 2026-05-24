# Cart Service

Flask microservice for shopping cart management with PostgreSQL persistence and Redis caching.

**Local Port:** `5003`

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Service health check |
| GET | `/cart` | Get cart for user |
| POST | `/cart/add` | Add item to cart |
| DELETE | `/cart/remove` | Remove item from cart |

All endpoints are also available under `/api/v1/cart/*` for gateway compatibility.

## User Identification

Pass `X-User-Id` header, `user_id` in JSON body, or `user_id` query param. Defaults to `guest`.

## Environment Variables

| Variable | Default |
|----------|---------|
| `PORT` | `5003` |
| `DATABASE_URL` | `postgresql://postgres:postgres@127.0.0.1:5432/ecommerce` |
| `REDIS_HOST` | `127.0.0.1` |
| `REDIS_PORT` | `6379` |

## Run Locally

```bash
cd services/cart
pip install -r requirements.txt
python run.py
```

## Docker

```bash
docker-compose up --build cart-service
```
