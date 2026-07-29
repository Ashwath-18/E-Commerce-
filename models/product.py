"""
Product Model
Represents a Product document in MongoDB
"""


class Product:
    def __init__(
        self,
        product_id,
        category,
        subcategory,
        brand,
        price,
        discount,
        final_price,
        stock,
        rating,
        review_count
    ):

        self.product_id = product_id
        self.category = category
        self.subcategory = subcategory
        self.brand = brand
        self.price = price
        self.discount = discount
        self.final_price = final_price
        self.stock = stock
        self.rating = rating
        self.review_count = review_count

    def to_dict(self):
        return {
            "product_id": self.product_id,
            "category": self.category,
            "subcategory": self.subcategory,
            "brand": self.brand,
            "price": self.price,
            "discount": self.discount,
            "final_price": self.final_price,
            "stock": self.stock,
            "rating": self.rating,
            "review_count": self.review_count
        }

    def __str__(self):
        return (
            f"Product("
            f"{self.product_id}, "
            f"{self.brand}, "
            f"{self.final_price})"
        )