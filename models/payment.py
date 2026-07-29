"""
Payment Model
Represents a Payment document in MongoDB
"""


class Payment:
    def __init__(self, user_id, product_id, payment_method):
        self.user_id = user_id
        self.product_id = product_id
        self.payment_method = payment_method

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "product_id": self.product_id,
            "payment_method": self.payment_method
        }

    def __str__(self):
        return f"Payment({self.payment_method})"