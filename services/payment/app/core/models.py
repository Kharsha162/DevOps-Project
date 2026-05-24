class PaymentEntity:
    def __init__(self, id, data):
        self.id = id
        self.data = data

    def to_dict(self):
        return {
            "id": self.id,
            "data": self.data,
            "type": "payment"
        }
