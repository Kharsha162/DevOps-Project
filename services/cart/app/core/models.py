class CartItem:
    def __init__(self, product_id, name, price, quantity, item_id=None):
        self.id = item_id
        self.product_id = product_id
        self.name = name
        self.price = float(price)
        self.quantity = int(quantity)

    def to_dict(self):
        item = {
            "product_id": self.product_id,
            "name": self.name,
            "price": self.price,
            "quantity": self.quantity,
        }
        if self.id:
            item["id"] = self.id
        return item


class Cart:
    def __init__(self, user_id, items=None):
        self.user_id = user_id
        self.items = items or []

    @property
    def total(self):
        return round(sum(item.price * item.quantity for item in self.items), 2)

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "items": [item.to_dict() for item in self.items],
            "total": self.total,
        }
