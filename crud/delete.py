"""
CRUD - Delete Operations

Every function returns True when a record was deleted and False when it
was not found. Deleting something that other records depend on raises
ValueError so the caller can show a meaningful message.
"""

from config.mongodb import db
from crud._utils import exact_ci

# MongoDB Collections
users = db["Users"]
products = db["Products"]
sellers = db["Sellers"]
orders = db["Orders"]


def delete_user(user_id):
    order_count = orders.count_documents({"user_id": exact_ci(user_id)})
    if order_count:
        raise ValueError(
            f"User has {order_count} order(s). Delete those orders first."
        )
    return users.delete_one({"user_id": exact_ci(user_id)}).deleted_count > 0


def delete_product(product_id):
    order_count = orders.count_documents({"product_id": exact_ci(product_id)})
    if order_count:
        raise ValueError(
            f"Product is used by {order_count} order(s). Delete those orders first."
        )

    deleted = products.delete_one(
        {"product_id": exact_ci(product_id)}
    ).deleted_count > 0

    if deleted:
        db["Inventory"].delete_many({"product_id": exact_ci(product_id)})
        db["Reviews"].delete_many({"product_id": exact_ci(product_id)})
    return deleted


def delete_seller(seller_id):
    return sellers.delete_one(
        {"seller_id": exact_ci(seller_id)}
    ).deleted_count > 0


def delete_order(user_id, product_id):
    return orders.delete_one({
        "user_id": exact_ci(user_id),
        "product_id": exact_ci(product_id),
    }).deleted_count > 0