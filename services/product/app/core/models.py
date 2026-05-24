class Product:
    def __init__(self, id, name, description, price, stock, category="general"):
        self.id = id
        self.name = name
        self.description = description
        self.price = float(price)
        self.stock = int(stock)
        self.category = category

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "stock": self.stock,
            "category": self.category
        }
