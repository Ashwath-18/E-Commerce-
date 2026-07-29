"""
Database Helper Functions
Reusable functions for inserting data into MongoDB
"""

from config.mongodb import db

# Collections
users = db["Users"]
products = db["Products"]
sellers = db["Sellers"]
categories = db["Categories"]
subcategories = db["SubCategories"]
orders = db["Orders"]
payments = db["Payments"]
shipping = db["Shipping"]
reviews = db["Reviews"]
inventory = db["Inventory"]
returns = db["Returns"]
order_items = db["OrderItems"]


# ---------------------------
# Users
# ---------------------------

def insert_user(data):
    if not users.find_one({"user_id": data["user_id"]}):
        users.insert_one(data)


# ---------------------------
# Products
# ---------------------------

def insert_product(data):
    if not products.find_one({"product_id": data["product_id"]}):
        products.insert_one(data)


# ---------------------------
# Sellers
# ---------------------------

def insert_seller(data):
    if not sellers.find_one({"seller_id": data["seller_id"]}):
        sellers.insert_one(data)


# ---------------------------
# Categories
# ---------------------------

def insert_category(data):
    if not categories.find_one({"category": data["category"]}):
        categories.insert_one(data)


# ---------------------------
# SubCategories
# ---------------------------

def insert_subcategory(data):
    if not subcategories.find_one({
        "category": data["category"],
        "subcategory": data["subcategory"]
    }):
        subcategories.insert_one(data)


# ---------------------------
# Orders
# ---------------------------

def insert_order(data):
    orders.insert_one(data)


# ---------------------------
# Payments
# ---------------------------

def insert_payment(data):
    payments.insert_one(data)


# ---------------------------
# Shipping
# ---------------------------

def insert_shipping(data):
    shipping.insert_one(data)


# ---------------------------
# Reviews
# ---------------------------

def insert_review(data):
    reviews.insert_one(data)


# ---------------------------
# Inventory
# ---------------------------

def insert_inventory(data):
    inventory.insert_one(data)


# ---------------------------
# Returns
# ---------------------------

def insert_return(data):
    returns.insert_one(data)


# ---------------------------
# Order Items
# ---------------------------

def insert_order_item(data):
    order_items.insert_one(data)