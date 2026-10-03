"""
CRUD - Update Operations
"""

from config.mongodb import db

# MongoDB Collections
products = db["Products"]
sellers = db["Sellers"]
orders = db["Orders"]


# -----------------------------
# Update Product Price (also recalculates final_price)
# -----------------------------
def update_product_price(product_id, new_price):

    product = products.find_one({"product_id": product_id})

    if not product:
        print("Product not found.")
        return

    discount = float(product.get("discount", 0) or 0)
    final_price = round(float(new_price) * (1 - discount / 100), 2)

    products.update_one(
        {"product_id": product_id},
        {"$set": {"price": new_price, "final_price": final_price}}
    )
    print("Product price updated successfully.")


# -----------------------------
# Update Product Stock (also syncs Inventory)
# -----------------------------
def update_product_stock(product_id, new_stock):

    result = products.update_one(
        {"product_id": product_id},
        {"$set": {"stock": new_stock}}
    )

    if result.matched_count == 0:
        print("Product not found.")
        return

    db["Inventory"].update_many(
        {"product_id": product_id},
        {"$set": {"stock": new_stock}}
    )
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
# Update Delivery Status (also syncs Shipping)
# -----------------------------
def update_delivery_status(user_id, product_id, new_status):

    key = {"user_id": user_id, "product_id": product_id}

    result = orders.update_one(key, {"$set": {"delivery_status": new_status}})

    if result.matched_count == 0:
        print("Order not found.")
        return

    db["Shipping"].update_many(key, {"$set": {"delivery_status": new_status}})
    print("Delivery status updated successfully.")