from config.mongodb import db

collections = [
    "Users",
    "Products",
    "Sellers",
    "Categories",
    "SubCategories",
    "Orders",
    "Payments",
    "Shipping",
    "Reviews",
    "Inventory",
    "Returns",
    "OrderItems"
]

for collection in collections:
    if collection not in db.list_collection_names():
        db.create_collection(collection)
        print(f"✅ {collection} collection created")
    else:
        print(f"⚠️ {collection} already exists")

print("\n All collections are ready.")
