import pandas as pd
from config.mongodb import db

# -------------------------------
# Load Excel Dataset
# -------------------------------

file_path = "dataset/amazon_ecommerce.xlsx"

try:
    df = pd.read_excel(file_path)
    print("✅ Dataset loaded successfully.")
    print(f"Total Records : {len(df)}")
except Exception as e:
    print("❌ Error loading dataset")
    print(e)
    exit()

# -------------------------------
# MongoDB Collections
# -------------------------------

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
orderitems = db["OrderItems"]

print("✅ MongoDB collections connected.")