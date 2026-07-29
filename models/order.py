"""
Order Model
Represents an Order document in MongoDB
"""


class Order:
    def __init__(
        self,
        user_id,
        product_id,
        purchase_date,
        payment_method,
        shipping_time_days,
        location,
        device,
        delivery_status,
        is_returned
    ):
        self.user_id = user_id
        self.product_id = product_id
        self.purchase_date = purchase_date
        self.payment_method = payment_method
        self.shipping_time_days = shipping_time_days
        self.location = location
        self.device = device
        self.delivery_status = delivery_status
        self.is_returned = is_returned

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "product_id": self.product_id,
            "purchase_date": self.purchase_date,
            "payment_method": self.payment_method,
            "shipping_time_days": self.shipping_time_days,
            "location": self.location,
            "device": self.device,
            "delivery_status": self.delivery_status,
            "is_returned": self.is_returned
        }

    def __str__(self):
        return (
            f"Order(User: {self.user_id}, "
            f"Product: {self.product_id}, "
            f"Status: {self.delivery_status})"
        )