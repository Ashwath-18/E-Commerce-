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

    if result.matched_count == 0:
        print("Product not found.")
    elif result.modified_count == 0:
        print("Price is already the same.")
    else:
        print("Product price updated successfully.")


# -----------------------------
# Update Product Stock
# -----------------------------
def update_product_stock(product_id, new_stock):

    result = products.update_one(
        {"product_id": product_id},
        {"$set": {"stock": new_stock}}
    )

    if result.matched_count == 0:
        print("Product not found.")
    elif result.modified_count == 0:
        print("Stock is already the same.")
    else:
        print("Product stock updated successfully.")


# -----------------------------
# Update Product Rating
# -----------------------------
def update_product_rating(product_id, new_rating):

    result = products.update_one(
        {"product_id": product_id},
        {"$set": {"rating": new_rating}}
    )

    if result.matched_count == 0:
        print("Product not found.")
    elif result.modified_count == 0:
        print("Rating is already the same.")
    else:
        print("Product rating updated successfully.")


# -----------------------------
# Update Seller Rating
# -----------------------------
def update_seller_rating(seller_id, new_rating):

    result = sellers.update_one(
        {"seller_id": seller_id},
        {"$set": {"seller_rating": new_rating}}
    )

    if result.matched_count == 0:
        print("Seller not found.")
    elif result.modified_count == 0:
        print("Seller rating is already the same.")
    else:
        print("Seller rating updated successfully.")


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

    if result.matched_count == 0:
        print("Order not found.")
    elif result.modified_count == 0:
        print("Delivery status is already the same.")
    else:
        print("Delivery status updated successfully.")