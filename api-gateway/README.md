# API Gateway

The API Gateway is the central reverse proxy routing external client HTTP requests to appropriate downstream services.

### Development Port: `5000`

### Core Features:
- Reverse Proxy Routing using HTTP requests forwarding.
- Resilience fallbacks if downstream is unavailable (sandbox simulator).
- Metric extraction & rate limiting interface.
