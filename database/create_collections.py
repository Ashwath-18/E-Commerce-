from config.mongodb import db

def create_collections():
    collections = [
        "users",
        "products",
        "sellers",
        "categories",
        "subcategories",
        "orders",
        "payments",
        "shipping",
        "reviews",
        "inventory",
        "returns",
        "orderitems"
    ]

    for collection in collections:
        if collection not in db.list_collection_names():
            db.create_collection(collection)
            print(f"✅ {collection} collection created")
        else:
            print(f"⚠️ {collection} already exists")

    print("\n All collections are ready.")

if __name__ == "__main__":
    create_collections()