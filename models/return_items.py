"""
Return Model
Represents a Return document in MongoDB
"""


class ReturnItem:
    def __init__(self, user_id, product_id, is_returned):
        self.user_id = user_id
        self.product_id = product_id
        self.is_returned = is_returned

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "product_id": self.product_id,
            "is_returned": self.is_returned
        }

    def __str__(self):
        return f"Return({self.is_returned})"