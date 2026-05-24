import uuid
import logging

logger = logging.getLogger(__name__)

class CreateProductUseCase:
    def __init__(self, product_repository, cache_client):
        self.repo = product_repository
        self.cache = cache_client

    def execute(self, name, description, price, stock, category):
        if not name or len(name) < 2:
            raise ValueError("Product name must be at least 2 characters long")
        if price is None or float(price) <= 0:
            raise ValueError("Product price must be greater than zero")
        if stock is None or int(stock) < 0:
            raise ValueError("Product stock cannot be negative")

        product = self.repo.create(name, description, price, stock, category)
        
        # Invalidate lists cache in Redis
        self.cache.delete("products:list:*")
        return product.to_dict()


class GetProductUseCase:
    def __init__(self, product_repository, cache_client):
        self.repo = product_repository
        self.cache = cache_client

    def execute(self, product_id):
        if not product_id:
            raise ValueError("Product ID is required")

        # 1. Read from Redis Cache first (Cache-aside)
        cache_key = f"product:{product_id}"
        cached_product = self.cache.get_product(cache_key)
        if cached_product:
            logger.info(f"Cache HIT for key: {cache_key}")
            return cached_product

        # 2. Cache miss: Read from database
        logger.info(f"Cache MISS for key: {cache_key}. Querying database...")
        product = self.repo.find_by_id(product_id)
        if not product:
            return None

        # 3. Write back to Redis Cache with a 10-minute expiry (600s)
        self.cache.set_product(cache_key, product.to_dict(), ttl=600)
        return product.to_dict()


class UpdateProductUseCase:
    def __init__(self, product_repository, cache_client):
        self.repo = product_repository
        self.cache = cache_client

    def execute(self, product_id, name=None, description=None, price=None, stock=None, category=None):
        if not product_id:
            raise ValueError("Product ID is required")

        # Check if exists
        product = self.repo.find_by_id(product_id)
        if not product:
            raise ValueError("Product not found")

        # Update and save
        updated_product = self.repo.update(product_id, name, description, price, stock, category)

        # Invalidate single product cache and lists cache (Cache Invalidation)
        self.cache.delete(f"product:{product_id}")
        self.cache.delete("products:list:*")

        return updated_product.to_dict()


class DeleteProductUseCase:
    def __init__(self, product_repository, cache_client):
        self.repo = product_repository
        self.cache = cache_client

    def execute(self, product_id):
        if not product_id:
            raise ValueError("Product ID is required")

        exists = self.repo.find_by_id(product_id)
        if not exists:
            raise ValueError("Product not found")

        self.repo.delete(product_id)

        # Invalidate cache keys (Cache Invalidation)
        self.cache.delete(f"product:{product_id}")
        self.cache.delete("products:list:*")
        return True


class ListProductsUseCase:
    def __init__(self, product_repository, cache_client):
        self.repo = product_repository
        self.cache = cache_client

    def execute(self, search_query=None, limit=10, offset=0):
        # Enforce limits
        limit = min(int(limit), 100)
        offset = max(int(offset), 0)

        # Try to read from cache (simple listing cache)
        cache_key = f"products:list:q_{search_query}:l_{limit}:o_{offset}"
        cached_list = self.cache.get_list(cache_key)
        if cached_list:
            logger.info(f"Cache HIT for list: {cache_key}")
            return cached_list

        logger.info(f"Cache MISS for list: {cache_key}. Querying database...")
        products = self.repo.find_all(search_query, limit, offset)
        
        result = [p.to_dict() for p in products]
        
        # Save to cache for 5 minutes
        self.cache.set_list(cache_key, result, ttl=300)
        return result
