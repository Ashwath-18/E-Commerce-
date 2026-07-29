"""
Shipping Model
Represents a Shipping document in MongoDB
"""


class Shipping:
    def __init__(
        self,
        user_id,
        product_id,
        shipping_time_days,
        location,
        delivery_status
    ):
        self.user_id = user_id
        self.product_id = product_id
        self.shipping_time_days = shipping_time_days
        self.location = location
        self.delivery_status = delivery_status

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "product_id": self.product_id,
            "shipping_time_days": self.shipping_time_days,
            "location": self.location,
            "delivery_status": self.delivery_status
        }

    def __str__(self):
        return f"Shipping({self.delivery_status})"