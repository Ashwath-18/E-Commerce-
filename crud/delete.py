"""
CRUD - Delete Operations
"""

from config.mongodb import db

# MongoDB Collections
users = db["Users"]
products = db["Products"]
sellers = db["Sellers"]
orders = db["Orders"]


# -----------------------------
# Delete User
# -----------------------------
def delete_user(user_id):

    result = users.delete_one({"user_id": user_id})

    if result.deleted_count:
        print("User deleted successfully.")
    else:
        print("User not found.")


# -----------------------------
# Delete Product
# -----------------------------
def delete_product(product_id):

    result = products.delete_one({"product_id": product_id})

    if result.deleted_count:
        print("Product deleted successfully.")
    else:
        print("Product not found.")


# -----------------------------
# Delete Seller
# -----------------------------
def delete_seller(seller_id):

    result = sellers.delete_one({"seller_id": seller_id})

    if result.deleted_count:
        print("Seller deleted successfully.")
    else:
        print("Seller not found.")


# -----------------------------
# Delete Order
# -----------------------------
def delete_order(user_id, product_id):

    result = orders.delete_one({
        "user_id": user_id,
        "product_id": product_id
    })

    if result.deleted_count:
        print("Order deleted successfully.")
    else:
        print("Order not found.")