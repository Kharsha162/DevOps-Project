# Production-Grade Cloud-Native E-Commerce DevOps Platform

Full-stack microservices platform with React frontend, Flask microservices, Docker, Kubernetes, Jenkins CI/CD, PostgreSQL, Redis, Prometheus, and Grafana.

## Architecture

```
Developer → Git/GitHub → Jenkins CI/CD → Docker → Kubernetes
                              ↓
React Frontend → API Gateway → Microservices (Auth, Product, Cart, Order, Payment, Notification)
                              ↓
                    PostgreSQL + Redis + Kafka
                              ↓
                    HPA Auto Scaling → Prometheus → Grafana
```

## Quick Start (Docker Compose)

```bash
docker compose up --build -d
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| API Gateway | http://localhost:5000 |
| Auth | http://localhost:5001 |
| Product | http://localhost:5002 |
| Cart | http://localhost:5003 |

## Kubernetes Deployment

```powershell
.\scripts\deploy-k8s.ps1
kubectl get pods -n ecommerce
```

## Verify Platform

```powershell
.\scripts\verify-platform.ps1
```

## Phase Completion Status

| Phase | Component | Status |
|-------|-----------|--------|
| 1 | Project Init + Git + GitHub | ✅ |
| 2 | Auth Service (JWT, PostgreSQL, Redis) | ✅ |
| 3 | Product Service (CRUD, search, cache) | ✅ |
| 4 | Cart Service (PostgreSQL, Redis cache) | ✅ |
| 5 | API Gateway (JWT, rate limiting, routing) | ✅ |
| 6 | React Frontend + Dashboard | ✅ |
| 7 | Docker Compose (healthchecks, networks) | ✅ |
| 8 | Kubernetes (deployments, secrets, PV/PVC) | ✅ |
| 9 | HPA Auto Scaling (CPU + memory) | ✅ |
| 10 | Prometheus + Grafana | ✅ |
| 11 | Jenkins CI/CD Pipeline | ✅ |

## API Examples

```bash
# Register
curl -X POST http://localhost:5000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","email":"demo@test.com","password":"secret123"}'

# Login
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"secret123"}'

# Products (public)
curl http://localhost:5000/api/v1/products

# Add to cart (JWT required)
curl -X POST http://localhost:5000/api/v1/cart/add \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"product_id":"p1","name":"Widget","price":9.99,"quantity":1}'
```

## Monitoring

- **Prometheus:** `kubectl port-forward svc/prometheus-service 9090:9090 -n ecommerce`
- **Grafana:** `kubectl port-forward svc/grafana-service 3001:3000 -n ecommerce` (admin / admin)

## Repository

https://github.com/Kharsha162/DevOps-Project
