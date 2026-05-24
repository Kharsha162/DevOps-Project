import logging

logger = logging.getLogger(__name__)


class GetCartUseCase:
    def __init__(self, cart_repo, cart_cache):
        self.cart_repo = cart_repo
        self.cart_cache = cart_cache

    def execute(self, user_id):
        if not user_id:
            raise ValueError("user_id is required")

        cached = self.cart_cache.get_cart(user_id)
        if cached is not None:
            logger.info("Cart cache hit for user %s", user_id)
            return cached

        cart = self.cart_repo.get_cart(user_id)
        cart_data = cart.to_dict()
        self.cart_cache.set_cart(user_id, cart_data)
        logger.info("Cart loaded from database for user %s", user_id)
        return cart_data


class AddToCartUseCase:
    def __init__(self, cart_repo, cart_cache, broker=None):
        self.cart_repo = cart_repo
        self.cart_cache = cart_cache
        self.broker = broker

    def execute(self, user_id, product_id, name, price, quantity=1):
        if not user_id:
            raise ValueError("user_id is required")
        if not product_id:
            raise ValueError("product_id is required")
        if not name:
            raise ValueError("name is required")
        if price is None or float(price) < 0:
            raise ValueError("price must be a non-negative number")
        if quantity is None or int(quantity) <= 0:
            raise ValueError("quantity must be greater than zero")

        cart = self.cart_repo.add_item(
            user_id=user_id,
            product_id=product_id,
            name=name,
            price=float(price),
            quantity=int(quantity),
        )
        cart_data = cart.to_dict()
        self.cart_cache.set_cart(user_id, cart_data)

        if self.broker:
            self.broker.send_event(
                "ecommerce-events",
                {
                    "event": "cart_item_added",
                    "user_id": user_id,
                    "product_id": product_id,
                    "quantity": int(quantity),
                },
            )

        logger.info("Added product %s to cart for user %s", product_id, user_id)
        return cart_data


class RemoveFromCartUseCase:
    def __init__(self, cart_repo, cart_cache, broker=None):
        self.cart_repo = cart_repo
        self.cart_cache = cart_cache
        self.broker = broker

    def execute(self, user_id, product_id, quantity=None):
        if not user_id:
            raise ValueError("user_id is required")
        if not product_id:
            raise ValueError("product_id is required")
        if quantity is not None and int(quantity) <= 0:
            raise ValueError("quantity must be greater than zero when provided")

        cart = self.cart_repo.remove_item(
            user_id=user_id,
            product_id=product_id,
            quantity=int(quantity) if quantity is not None else None,
        )
        cart_data = cart.to_dict()
        self.cart_cache.set_cart(user_id, cart_data)

        if self.broker:
            self.broker.send_event(
                "ecommerce-events",
                {
                    "event": "cart_item_removed",
                    "user_id": user_id,
                    "product_id": product_id,
                    "quantity": quantity,
                },
            )

        logger.info("Removed product %s from cart for user %s", product_id, user_id)
        return cart_data
