from config.mongodb import db

def create_indexes():
    indexes = {
        "Users": [
            ("user_id", True)
        ],
        "Products": [
            ("product_id", True),
            ("brand", False),
        ("category_id", False)
        ],

        "Orders": [
            ("order_id", True),
            ("user_id", False),
            ("purchase_date", False)
        ],
        "Sellers": [
            ("seller_id", True)
        ],

        "Reviews": [
            ("review_id", True),
            ("product_id", False)
        ]
    }

    print("Creating Indexes...\n")

    for collection_name, fields in indexes.items():

        collection = db[collection_name]

        for field, unique in fields:

            collection.create_index(field, unique=unique)

            print(f"{collection_name} -> {field}")

    print("\n✅ All indexes created successfully.")

if __name__ == "__main__":
    create_indexes()