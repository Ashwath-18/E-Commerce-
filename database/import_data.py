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
    df = pd.read_csv("data/amazon_dataset_half.csv")

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

print("✅ Ready to Import Data...")