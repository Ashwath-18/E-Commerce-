"""
Seller Model
Represents a Seller document in MongoDB
"""


class Seller:
    def __init__(self, seller_id, seller_rating):
        self.seller_id = seller_id
        self.seller_rating = seller_rating

    def to_dict(self):
        return {
            "seller_id": self.seller_id,
            "seller_rating": self.seller_rating
        }

    def __str__(self):
        return f"Seller({self.seller_id}, Rating: {self.seller_rating})"