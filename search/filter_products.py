"""
Filter Operations
"""

from config.mongodb import db

products = db["Products"]
orders = db["Orders"]

# -----------------------------
# Filter Products by Minimum Rating
# -----------------------------
def filter_products_by_rating(min_rating):

    result = list(
        products.find(
            {
                "rating": {
                    "$gte": min_rating
                }
            },
            {"_id": 0}
        )
    )

    return result
# -----------------------------
# Filter Products by Price Range
# -----------------------------
def filter_products_by_price(min_price, max_price):

    result = list(
        products.find(
            {
                "price": {
                    "$gte": min_price,
                    "$lte": max_price
                }
            },
            {"_id": 0}
        )
    )

    return result
# -----------------------------
# Filter Products In Stock
# -----------------------------
def filter_products_in_stock():

    result = list(
        products.find(
            {
                "stock": {
                    "$gt": 0
                }
            },
            {"_id": 0}
        )
    )

    return result
# -----------------------------
# Filter Returned Orders
# -----------------------------
def filter_returned_orders():

    result = list(
        orders.find(
            {
                "is_returned": True
            },
            {"_id": 0}
        )
    )

    return result
# -----------------------------
# Filter Delivered Orders
# -----------------------------
def filter_delivered_orders():

    result = list(
        orders.find(
            {
                "delivery_status": "Delivered"
            },
            {"_id": 0}
        )
    )

    return result
# -----------------------------
# Filter Orders by Payment Method
# -----------------------------
def filter_orders_by_payment(payment_method):

    result = list(
        orders.find(
            {
                "payment_method": payment_method
            },
            {"_id": 0}
        )
    )

    return result
