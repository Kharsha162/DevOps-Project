# Product Service

Manages product inventories, product listings, catalog items, and search operations.

### Local Port: `5002`

## API Endpoints

- `GET /products?search=<term>&limit=<n>&offset=<n>`
- `GET /product/<id>`
- `POST /product`
- `PUT /product/<id>`
- `DELETE /product/<id>`
- `GET /health`

## Local Docker Compose

```bash
docker compose up --build postgres redis kafka product-service
```

## Example curl commands

Create a product:
```bash
curl -X POST http://localhost:5002/product \
  -H 'Content-Type: application/json' \
  -d '{"name":"Test Product","description":"A product","price":25.5,"stock":10,"category":"general"}'
```

List products:
```bash
curl 'http://localhost:5002/products?limit=10&offset=0'
```

Get by id:
```bash
curl http://localhost:5002/product/<id>
```

Update product:
```bash
curl -X PUT http://localhost:5002/product/<id> \
  -H 'Content-Type: application/json' \
  -d '{"price":29.99,"stock":12}'
```

Delete product:
```bash
curl -X DELETE http://localhost:5002/product/<id>
```

Health check:
```bash
curl http://localhost:5002/health
```
