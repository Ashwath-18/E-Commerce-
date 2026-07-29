"""
CRUD - Update Operations
"""

from config.mongodb import db

# MongoDB Collections
products = db["Products"]
sellers = db["Sellers"]
orders = db["Orders"]


# -----------------------------
# Update Product Price
# -----------------------------
def update_product_price(product_id, new_price):

    result = products.update_one(
        {"product_id": product_id},
        {"$set": {"price": new_price}}
    )

    if result.modified_count:
        print("Product price updated successfully.")
    else:
        print("Product not found or price unchanged.")


# -----------------------------
# Update Product Stock
# -----------------------------
def update_product_stock(product_id, new_stock):

    result = products.update_one(
        {"product_id": product_id},
        {"$set": {"stock": new_stock}}
    )

    if result.modified_count:
        print("Product stock updated successfully.")
    else:
        print("Product not found or stock unchanged.")


# -----------------------------
# Update Product Rating
# -----------------------------
def update_product_rating(product_id, new_rating):

    result = products.update_one(
        {"product_id": product_id},
        {"$set": {"rating": new_rating}}
    )

    if result.modified_count:
        print("Product rating updated successfully.")
    else:
        print("Product not found or rating unchanged.")


# -----------------------------
# Update Seller Rating
# -----------------------------
def update_seller_rating(seller_id, new_rating):

    result = sellers.update_one(
        {"seller_id": seller_id},
        {"$set": {"seller_rating": new_rating}}
    )

    if result.modified_count:
        print("Seller rating updated successfully.")
    else:
        print("Seller not found or rating unchanged.")


# -----------------------------
# Update Delivery Status
# -----------------------------
def update_delivery_status(user_id, product_id, new_status):

    result = orders.update_one(
        {
            "user_id": user_id,
            "product_id": product_id
        },
        {
            "$set": {
                "delivery_status": new_status
            }
        }
    )

    if result.modified_count:
        print("Delivery status updated successfully.")
    else:
        print("Order not found or status unchanged.")