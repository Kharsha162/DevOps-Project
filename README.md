# Production-Grade Cloud-Native E-Commerce Platform

Welcome to the Cloud-Native E-Commerce platform. This platform is built using a highly resilient microservices architecture, clean domain-driven architecture, and industry-standard DevOps tools.

## Architecture Topology

```
                  [ Users ]
                      ↓
               [ React Frontend ] (Port 3000)
                      ↓
               [ NGINX Ingress ]
                      ↓
               [ API Gateway ] (Port 5000)
                      ↓
   +------------------+------------------+------------------+------------------+
   ↓                  ↓                  ↓                  ↓                  ↓
[Auth] (5001)    [Product] (5002)   [Cart] (5003)      [Order] (5004)    [Payment] (5005)
   ↓                  ↓                  ↓                  ↓                  ↓
 [Redis]         [Postgres]          [Redis]           [Postgres]          [Kafka]
                                                                               ↓
                                                                        [Notification] (5006)
```

## Service Details & Port Map

| Component | Port | Description | DB / Cache | Messaging |
| :--- | :---: | :--- | :--- | :--- |
| **React Frontend** | `3000` | UI Dashboard & E-Commerce Flow | - | - |
| **API Gateway** | `5000` | Central Entry point, routes downstream | - | - |
| **Auth Service** | `5001` | JWT creation, verification & user admin | Redis | - |
| **Product Service** | `5002` | Catalog management, updates & caching | PostgreSQL | - |
| **Cart Service** | `5003` | Add/Remove items, ephemeral state | Redis | - |
| **Order Service** | `5004` | Order placement, tracking & updates | PostgreSQL | Kafka (Producer) |
| **Payment Service** | `5005` | Processing payments, stripe simulator | PostgreSQL | Kafka (Producer) |
| **Notification Service** | `5006` | Email / SMS dispatcher | - | Kafka (Consumer) |

## Getting Started Locally

### Prerequisites
* Python 3.13+
* Node.js & npm (for frontend)
* Docker & docker-compose

### Running Services Directly
To start the services locally for validation, you can use the verification runner script or start them manually.
Run this in separate shell windows:

```powershell
# In root directory
python -m venv venv
.\venv\Scripts\activate
pip install -r api-gateway/requirements.txt
python api-gateway/run.py
```
Do the same for each service in `services/<service_name>/`.

### Running with Docker Compose
```bash
docker-compose up --build
```
