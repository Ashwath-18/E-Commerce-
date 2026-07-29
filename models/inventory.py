"""
Inventory Model
Represents an Inventory document in MongoDB
"""


class Inventory:
    def __init__(self, product_id, stock):
        self.product_id = product_id
        self.stock = stock

    def to_dict(self):
        return {
            "product_id": self.product_id,
            "stock": self.stock
        }

    def __str__(self):
        return f"Inventory({self.stock})"