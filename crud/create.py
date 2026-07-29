"""
CRUD - Create Operations
"""

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


# -----------------------------
# Create User
# -----------------------------
def create_user(user_id):
    if users.find_one({"user_id": user_id}):
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

    if products.find_one({"product_id": product_id}):
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

    if sellers.find_one({"seller_id": seller_id}):
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