"""Case-insensitive search operations for Cartify collections."""

import re

from config.mongodb import db

products = db["Products"]
orders = db["Orders"]
sellers = db["Sellers"]
users = db["Users"]
shipping = db["Shipping"]


def _text_query(value):
    """Return a safe, case-insensitive partial-match MongoDB query."""
    return {"$regex": re.escape(str(value).strip()), "$options": "i"}


def _exact_text_query(value):
    """Return a safe, case-insensitive exact-match query."""
    return {"$regex": f"^{re.escape(str(value).strip())}$", "$options": "i"}

# -----------------------------
# Search Product by Product ID
# -----------------------------
def search_product_by_id(product_id):

    product = products.find_one(
        {"product_id": _exact_text_query(product_id)},
        {"_id": 0}
    )

    if product:
        return product

    return None

# -----------------------------
# Search Products by Brand
# -----------------------------
def search_products_by_brand(brand):

    result = list(
        products.find(
            {"brand": _text_query(brand)},
            {"_id": 0}
        )
    )

    if result:
        return result

    return []

# -----------------------------
# Search Products by Category
# -----------------------------
def search_products_by_category(category):

    result = list(
        products.find(
            {"category": _text_query(category)},
            {"_id": 0}
        )
    )

    if result:
        return result

    return []

# -----------------------------
# Search Products by Subcategory
# -----------------------------
def search_products_by_subcategory(subcategory):

    result = list(
        products.find(
            {"subcategory": _text_query(subcategory)},
            {"_id": 0}
        )
    )

    if result:
        return result

    return []

# -----------------------------
# Search Products by Price Range
# -----------------------------
def search_products_by_price_range(min_price, max_price):

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

    if result:
        return result

    return []

# -----------------------------
# Search Products by Minimum Rating
# -----------------------------
def search_products_by_rating(min_rating):

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

    if result:
        return result

    return []

# -----------------------------
# Search Orders by User ID
# -----------------------------
def search_orders_by_user(user_id):

    result = list(
        orders.find(
            {"user_id": _text_query(user_id)},
            {"_id": 0}
        )
    )

    if result:
        return result

    return []

# -----------------------------
# Search Sellers by Minimum Rating
# -----------------------------
def search_sellers_by_rating(min_rating):

    result = list(
        sellers.find(
            {
                "seller_rating": {
                    "$gte": min_rating
                }
            },
            {"_id": 0}
        )
    )

    if result:
        return result

    return []


# -----------------------------
# Search Products Across Key Fields
# -----------------------------
def search_products(query):
    """Search product ID, brand, category, and subcategory in one query."""
    text_query = _text_query(query)
    return list(
        products.find(
            {
                "$or": [
                    {"product_id": text_query},
                    {"brand": text_query},
                    {"category": text_query},
                    {"subcategory": text_query},
                ]
            },
            {"_id": 0},
        )
    )


# -----------------------------
# Search Users by User ID
# -----------------------------
def search_users_by_id(user_id):
    return list(users.find({"user_id": _text_query(user_id)}, {"_id": 0}))


# -----------------------------
# Search Shipping Records
# -----------------------------
def search_shipping(query):
    """Search common shipping text fields without matching letter case."""
    text_query = _text_query(query)
    return list(
        shipping.find(
            {
                "$or": [
                    {"user_id": text_query},
                    {"product_id": text_query},
                    {"location": text_query},
                    {"delivery_status": text_query},
                ]
            },
            {"_id": 0},
        )
    )


# -----------------------------
# Product Detail Overview
# -----------------------------
def get_product_overview(product_id):
    """Return a product and summary data from all linked collections."""
    product = search_product_by_id(product_id)
    if not product:
        return None

    product_id = product["product_id"]
    match = {"product_id": product_id}

    inventory = db["Inventory"].find_one(match, {"_id": 0}) or {}
    reviews = list(db["Reviews"].find(match, {"_id": 0}))
    shipping_records = list(db["Shipping"].find(match, {"_id": 0}))
    payments = list(db["Payments"].find(match, {"_id": 0}))

    return {
        "product": product,
        "inventory_stock": inventory.get("stock", product.get("stock", 0)),
        "review_records": len(reviews),
        "average_review_rating": (
            round(sum(review.get("rating", 0) for review in reviews) / len(reviews), 2)
            if reviews else None
        ),
        "order_count": db["Orders"].count_documents(match),
        "shipping_count": len(shipping_records),
        "delivery_statuses": sorted(
            {record.get("delivery_status") for record in shipping_records if record.get("delivery_status")}
        ),
        "payment_count": len(payments),
        "payment_methods": sorted(
            {payment.get("payment_method") for payment in payments if payment.get("payment_method")}
        ),
        "return_count": db["Returns"].count_documents({**match, "is_returned": True}),
        "order_item_count": db["OrderItems"].count_documents(match),
    }


# -----------------------------
# User Detail Overview
# -----------------------------
def get_user_overview(user_id):
    """Return a user and summary data from all linked collections."""
    user = users.find_one({"user_id": _exact_text_query(user_id)}, {"_id": 0})
    if not user:
        return None

    user_id = user["user_id"]
    match = {"user_id": user_id}
    orders_for_user = list(db["Orders"].find(match, {"_id": 0}))
    shipping_records = list(db["Shipping"].find(match, {"_id": 0}))
    payments = list(db["Payments"].find(match, {"_id": 0}))

    return {
        "user": user,
        "orders": orders_for_user,
        "unique_products": len(
            {order.get("product_id") for order in orders_for_user if order.get("product_id")}
        ),
        "shipping_count": len(shipping_records),
        "delivery_statuses": sorted(
            {record.get("delivery_status") for record in shipping_records if record.get("delivery_status")}
        ),
        "payment_count": len(payments),
        "payment_methods": sorted(
            {payment.get("payment_method") for payment in payments if payment.get("payment_method")}
        ),
        "return_count": db["Returns"].count_documents({**match, "is_returned": True}),
        "order_item_count": db["OrderItems"].count_documents(match),
    }

