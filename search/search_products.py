"""Case-insensitive search operations for Cartify collections."""

import re

from config.mongodb import db

products = db["Products"]
orders = db["Orders"]
sellers = db["Sellers"]
users = db["Users"]
shipping = db["Shipping"]
reviews = db["Reviews"]


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
# Search and Filter Orders
# -----------------------------
def search_orders(query="", from_date=None, to_date=None):
    """Search order text fields and optionally filter an ISO date range."""
    filters = []
    query = str(query).strip()

    if query:
        text_query = _text_query(query)
        text_filters = [
            {"user_id": text_query},
            {"product_id": text_query},
            {"payment_method": text_query},
            {"delivery_status": text_query},
        ]

        return_values = {
            "returned": True,
            "return": True,
            "true": True,
            "yes": True,
            "not returned": False,
            "false": False,
            "no": False,
        }
        returned_value = return_values.get(query.casefold())
        if returned_value is not None:
            text_filters.append({"is_returned": returned_value})

        filters.append({"$or": text_filters})

    date_filter = {}
    if from_date:
        date_filter["$gte"] = from_date
    if to_date:
        date_filter["$lte"] = to_date
    if date_filter:
        filters.append({"purchase_date": date_filter})

    if not filters:
        criteria = {}
    elif len(filters) == 1:
        criteria = filters[0]
    else:
        criteria = {"$and": filters}

    return list(orders.find(criteria, {"_id": 0}))


def search_orders_by_user(user_id):
    """Preserve the focused user-ID search used by the global Search page."""
    return list(orders.find({"user_id": _text_query(user_id)}, {"_id": 0}))

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


def search_reviews(query):
    """Search review records by product ID without matching letter case."""
    return list(reviews.find({"product_id": _text_query(query)}, {"_id": 0}))


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


# -----------------------------
# Paginated Collection Queries
# -----------------------------
def _get_page(collection, criteria, page, page_size):
    """Fetch one database page without materialising the full result set."""
    page = max(1, int(page))
    total = collection.count_documents(criteria)
    records = list(
        collection.find(criteria, {"_id": 0})
        .skip((page - 1) * page_size)
        .limit(page_size)
    )
    return records, total


def get_products_page(page, page_size, query=""):
    if query:
        text_query = _text_query(query)
        criteria = {
            "$or": [
                {"product_id": text_query},
                {"brand": text_query},
                {"category": text_query},
                {"subcategory": text_query},
            ]
        }
    else:
        criteria = {}
    return _get_page(products, criteria, page, page_size)


def get_users_page(page, page_size, query=""):
    criteria = {"user_id": _text_query(query)} if query else {}
    return _get_page(users, criteria, page, page_size)


def get_shipping_page(page, page_size, query=""):
    if query:
        text_query = _text_query(query)
        criteria = {
            "$or": [
                {"user_id": text_query},
                {"product_id": text_query},
                {"location": text_query},
                {"delivery_status": text_query},
            ]
        }
    else:
        criteria = {}
    return _get_page(shipping, criteria, page, page_size)


def get_reviews_page(page, page_size, query=""):
    criteria = {"product_id": _text_query(query)} if query else {}
    return _get_page(reviews, criteria, page, page_size)


def get_orders_page(page, page_size, query="", from_date=None, to_date=None):
    filters = []
    query = str(query).strip()

    if query:
        text_query = _text_query(query)
        text_filters = [
            {"user_id": text_query},
            {"product_id": text_query},
            {"payment_method": text_query},
            {"delivery_status": text_query},
        ]
        return_values = {
            "returned": True, "return": True, "true": True, "yes": True,
            "not returned": False, "false": False, "no": False,
        }
        returned_value = return_values.get(query.casefold())
        if returned_value is not None:
            text_filters.append({"is_returned": returned_value})
        filters.append({"$or": text_filters})

    date_filter = {}
    if from_date:
        date_filter["$gte"] = from_date
    if to_date:
        date_filter["$lte"] = to_date
    if date_filter:
        filters.append({"purchase_date": date_filter})

    criteria = {} if not filters else filters[0] if len(filters) == 1 else {"$and": filters}
    return _get_page(orders, criteria, page, page_size)


def get_search_results_page(mode, query, page, page_size):
    """Fetch one page for a Search & Filter mode."""
    if mode == "Products by Brand":
        return _get_page(products, {"brand": _text_query(query)}, page, page_size)
    if mode == "Products by Category":
        return _get_page(products, {"category": _text_query(query)}, page, page_size)
    if mode == "Products by Subcategory":
        return _get_page(products, {"subcategory": _text_query(query)}, page, page_size)
    if mode == "Products by Min Rating":
        return _get_page(products, {"rating": {"$gte": float(query)}}, page, page_size)
    if mode == "Orders by User ID":
        return _get_page(orders, {"user_id": _text_query(query)}, page, page_size)
    if mode == "User by ID":
        return _get_page(orders, {"user_id": _exact_text_query(query)}, page, page_size)
    if mode == "Sellers by Min Rating":
        return _get_page(sellers, {"seller_rating": {"$gte": float(query)}}, page, page_size)
    if mode == "In-Stock Products":
        return _get_page(products, {"stock": {"$gt": 0}}, page, page_size)
    if mode == "Returned Orders":
        return _get_page(orders, {"is_returned": True}, page, page_size)
    if mode == "Delivered Orders":
        return _get_page(orders, {"delivery_status": "Delivered"}, page, page_size)
    return [], 0

