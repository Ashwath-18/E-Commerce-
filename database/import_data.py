"""
Import CSV Data into MongoDB
"""

import pandas as pd

from models.user import User
from models.product import Product
from models.seller import Seller
from models.order import Order
from models.category import Category
from models.subcategory import SubCategory
from models.payment import Payment
from models.shipping import Shipping
from models.review import Review
from models.inventory import Inventory
from models.return_item import ReturnItem
from models.order_item import OrderItem

from database.helpers import (
    insert_user,
    insert_product,
    insert_seller,
    insert_category,
    insert_subcategory,
    insert_order,
    insert_payment,
    insert_shipping,
    insert_review,
    insert_inventory,
    insert_return,
    insert_order_item
)

# ----------------------------------
# Load Dataset
# ----------------------------------

try:
    df = pd.read_csv("data/amazon_dataset_half.csv").head(10000)

    print("✅ Dataset Loaded Successfully")
    print(f"Total Records : {len(df)}")

except Exception as e:
    print("❌ Error Loading Dataset")
    print(e)
    exit()

# ----------------------------------
# Duplicate Tracking
# ----------------------------------

user_ids = set()
product_ids = set()
seller_ids = set()
categories = set()
subcategories = set()

print("✅ Ready to Import Data...\n")

# ----------------------------------
# Import Loop
# ----------------------------------

count = 0

for _, row in df.iterrows():

    try:

        # -----------------------------
        # Read Values
        # -----------------------------

        user_id = row["user_id"]
        product_id = row["product_id"]

        category = row["category"]
        subcategory = row["subcategory"]

        brand = row["brand"]

        price = float(row["price"])
        discount = float(row["discount"])
        final_price = float(row["final_price"])

        stock = int(row["stock"])

        rating = float(row["rating"])
        review_count = int(row["review_count"])

        seller_id = row["seller_id"]
        seller_rating = float(row["seller_rating"])

        purchase_date = row["purchase_date"]

        shipping_time_days = int(row["shipping_time_days"])

        location = row["location"]
        device = row["device"]

        payment_method = row["payment_method"]

        is_returned = str(row["is_returned"]).strip().lower() == "true"

        delivery_status = row["delivery_status"]

        # -----------------------------
        # Users
        # -----------------------------

        if user_id not in user_ids:

            user = User(user_id)

            insert_user(user.to_dict())

            user_ids.add(user_id)

        # -----------------------------
        # Categories
        # -----------------------------

        if category not in categories:

            category_obj = Category(category)

            insert_category(category_obj.to_dict())

            categories.add(category)

        # -----------------------------
        # Sub Categories
        # -----------------------------

        sub_key = (category, subcategory)

        if sub_key not in subcategories:

            subcategory_obj = SubCategory(
                category,
                subcategory
            )

            insert_subcategory(subcategory_obj.to_dict())

            subcategories.add(sub_key)

        # -----------------------------
        # Sellers
        # -----------------------------

        if seller_id not in seller_ids:

            seller = Seller(
                seller_id,
                seller_rating
            )

            insert_seller(seller.to_dict())

            seller_ids.add(seller_id)

        # -----------------------------
        # Products
        # -----------------------------

        if product_id not in product_ids:

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

            insert_product(product.to_dict())

            product_ids.add(product_id)

        # -----------------------------
        # Orders
        # -----------------------------

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

        insert_order(order.to_dict())

        # -----------------------------
        # Payments
        # -----------------------------

        payment = Payment(
            user_id,
            product_id,
            payment_method
        )

        insert_payment(payment.to_dict())
                # -----------------------------
        # Shipping
        # -----------------------------

        shipping = Shipping(
            user_id,
            product_id,
            shipping_time_days,
            location,
            delivery_status
        )

        insert_shipping(shipping.to_dict())

        # -----------------------------
        # Reviews
        # -----------------------------

        review = Review(
            product_id,
            rating,
            review_count
        )

        insert_review(review.to_dict())

        # -----------------------------
        # Inventory
        # -----------------------------

        inventory = Inventory(
            product_id,
            stock
        )

        insert_inventory(inventory.to_dict())

        # -----------------------------
        # Returns
        # -----------------------------

        return_item = ReturnItem(
            user_id,
            product_id,
            is_returned
        )

        insert_return(return_item.to_dict())

        # -----------------------------
        # Order Items
        # -----------------------------

        order_item = OrderItem(
            user_id,
            product_id
        )

        insert_order_item(order_item.to_dict())

        count += 1

        if count % 5000 == 0:
            print(f"✅ Imported {count} records...")

    except Exception as e:
        print(f"❌ Error importing row {count + 1}")
        print(e)

print("\n===================================")
print("🎉 DATA IMPORT COMPLETED")
print("===================================")
print(f"Total Records Imported : {count}")

print(f"Unique Users          : {len(user_ids)}")
print(f"Unique Products       : {len(product_ids)}")
print(f"Unique Sellers        : {len(seller_ids)}")
print(f"Unique Categories     : {len(categories)}")
print(f"Unique SubCategories  : {len(subcategories)}")
print("===================================")