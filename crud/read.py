"""
CRUD - Read Operations
"""

from config.mongodb import db

# MongoDB Collections
users = db["Users"]
products = db["Products"]
sellers = db["Sellers"]
orders = db["Orders"]


# -----------------------------
# Read User by ID
# -----------------------------
def get_user(user_id):
    user = users.find_one({"user_id": user_id}, {"_id": 0})

    if user:
        return user

    return None


# -----------------------------
# Read Product by ID
# -----------------------------
def get_product(product_id):
    product = products.find_one({"product_id": product_id}, {"_id": 0})

    if product:
        return product

    return None


# -----------------------------
# Read Seller by ID
# -----------------------------
def get_seller(seller_id):
    seller = sellers.find_one({"seller_id": seller_id}, {"_id": 0})

    if seller:
        return seller

    return None


# -----------------------------
# Read All Users
# -----------------------------
def get_all_users():
    return list(users.find({}, {"_id": 0}))


# -----------------------------
# Read All Products
# -----------------------------
def get_all_products():
    return list(products.find({}, {"_id": 0}))


# -----------------------------
# Read All Sellers
# -----------------------------
def get_all_sellers():
    return list(sellers.find({}, {"_id": 0}))


# -----------------------------
# Read All Orders
# -----------------------------
def get_all_orders():
    return list(orders.find({}, {"_id": 0}))