"""
Search Operations - Products
"""

from config.mongodb import db

products = db["Products"]
orders = db["Orders"]
sellers = db["Sellers"]

# -----------------------------
# Search Product by Product ID
# -----------------------------
def search_product_by_id(product_id):

    product = products.find_one(
        {"product_id": product_id},
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
            {"brand": brand},
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
            {"category": category},
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
            {"subcategory": subcategory},
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
            {"user_id": user_id},
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

