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
    users.insert_many(data)


# ---------------------------
# Products
# ---------------------------

def insert_product(data):
    products.insert_many(data)


# ---------------------------
# Sellers
# ---------------------------

def insert_seller(data):
    sellers.insert_many(data)


# ---------------------------
# Categories
# ---------------------------

def insert_category(data):
    categories.insert_many(data)


# ---------------------------
# SubCategories
# ---------------------------

def insert_subcategory(data):
    subcategories.insert_many(data)

# ---------------------------
# Orders
# ---------------------------

def insert_order(data):
    orders.insert_many(data)


# ---------------------------
# Payments
# ---------------------------

def insert_payment(data):
    payments.insert_many(data)


# ---------------------------
# Shipping
# ---------------------------

def insert_shipping(data):
    shipping.insert_many(data)


# ---------------------------
# Reviews
# ---------------------------

def insert_review(data):
    reviews.insert_many(data)


# ---------------------------
# Inventory
# ---------------------------

def insert_inventory(data):
    inventory.insert_many(data)


# ---------------------------
# Returns
# ---------------------------

def insert_return(data):
    returns.insert_many(data)


# ---------------------------
# Order Items
# ---------------------------

def insert_order_item(data):
    order_items.insert_many(data)