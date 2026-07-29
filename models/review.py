"""
Review Model
Represents a Review document in MongoDB
"""


class Review:
    def __init__(self, product_id, rating, review_count):
        self.product_id = product_id
        self.rating = rating
        self.review_count = review_count

    def to_dict(self):
        return {
            "product_id": self.product_id,
            "rating": self.rating,
            "review_count": self.review_count
        }

    def __str__(self):
        return f"Review({self.rating})"