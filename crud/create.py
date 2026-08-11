"""CRUD create operations with consistent input normalization."""

import re

from config.mongodb import db
from models.user import User
from models.product import Product
from models.seller import Seller
from models.order import Order

# MongoDB Collections
users = db["Users"]
products = db["Products"]
sellers = db["Sellers"]
orders = db["Orders"]


def _exact_case_insensitive(value):
    """Build a safe exact-match query that ignores input letter case."""
    return {"$regex": f"^{re.escape(str(value).strip())}$", "$options": "i"}


def _normalize_id(value):
    """Store IDs in the same uppercase format as the imported dataset."""
    return str(value).strip().upper()


def _normalize_product_label(field, value):
    """Reuse the dataset's spelling/case when a matching label already exists."""
    cleaned_value = " ".join(str(value).strip().split())
    if not cleaned_value:
        return ""

    existing = products.find_one(
        {field: _exact_case_insensitive(cleaned_value)},
        {field: 1, "_id": 0},
    )
    if existing:
        return existing[field]

    return cleaned_value.title()


# -----------------------------
# Create User
# -----------------------------
def create_user(user_id):
    user_id = _normalize_id(user_id)

    if users.find_one({"user_id": _exact_case_insensitive(user_id)}):
        print(f"User {user_id} already exists.")
        return

    user = User(user_id)
    users.insert_one(user.to_dict())
    print(f"User {user_id} inserted successfully.")


# -----------------------------
# Create Product
# -----------------------------
def create_product(
    product_id,
    category,
    subcategory,
    brand,
    price,
    discount,
    final_price,
    stock,
    rating,
    review_count
):
    product_id = _normalize_id(product_id)
    category = _normalize_product_label("category", category)
    subcategory = _normalize_product_label("subcategory", subcategory)
    brand = _normalize_product_label("brand", brand)

    if products.find_one({"product_id": _exact_case_insensitive(product_id)}):
        print(f"Product {product_id} already exists.")
        return

    product = Product(
        product_id,
        category,
        subcategory,
        brand,
        price,
        discount,
        final_price,
        stock,
        rating,
        review_count
    )

    products.insert_one(product.to_dict())
    print(f"Product {product_id} inserted successfully.")


# -----------------------------
# Create Seller
# -----------------------------
def create_seller(seller_id, seller_rating):
    seller_id = _normalize_id(seller_id)

    if sellers.find_one({"seller_id": _exact_case_insensitive(seller_id)}):
        print(f"Seller {seller_id} already exists.")
        return

    seller = Seller(seller_id, seller_rating)

    sellers.insert_one(seller.to_dict())
    print(f"Seller {seller_id} inserted successfully.")


# -----------------------------
# Create Order
# -----------------------------
def create_order(
    user_id,
    product_id,
    purchase_date,
    payment_method,
    shipping_time_days,
    location,
    device,
    delivery_status,
    is_returned
):
    user_id = _normalize_id(user_id)
    product_id = _normalize_id(product_id)

    order = Order(
        user_id,
        product_id,
        purchase_date,
        payment_method,
        shipping_time_days,
        location,
        device,
        delivery_status,
        is_returned
    )

    orders.insert_one(order.to_dict())
    print("Order inserted successfully.")
