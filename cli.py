from crud.create import *
from crud.read import *
from crud.update import *
from crud.delete import *
from search.search import search_menu


def _report(deleted, name):
    print(f"{name} deleted successfully." if deleted else f"{name} not found.")


def _safe(menu):
    """Run a menu; show validation errors instead of crashing the CLI."""
    try:
        menu()
    except (ValueError, TypeError) as exc:
        print(f"Error: {exc}")


def create_menu():
    while True:
        print("\n========== CREATE MENU ==========")
        print("1. Create User")
        print("2. Create Product")
        print("3. Create Seller")
        print("4. Create Order")
        print("5. Back")

        choice = input("Enter choice: ")

        if choice == "1":
            user_id = input("User ID: ")
            create_user(user_id)

        elif choice == "2":
            product_id = input("Product ID: ")
            category = input("Category: ")
            subcategory = input("Subcategory: ")
            brand = input("Brand: ")
            price = float(input("Price: "))
            discount = float(input("Discount: "))
            final_price = float(input("Final Price: "))
            stock = int(input("Stock: "))
            rating = float(input("Rating: "))
            review_count = int(input("Review Count: "))

            create_product(
                product_id,
                category,
                subcategory,
                brand,
                price,
                discount,
                final_price,
                stock,
                rating,
                review_count,
            )

        elif choice == "3":
            seller_id = input("Seller ID: ")
            seller_rating = float(input("Seller Rating: "))
            create_seller(seller_id, seller_rating)

        elif choice == "4":
            user_id = input("User ID: ")
            product_id = input("Product ID: ")
            purchase_date = input("Purchase Date (YYYY-MM-DD): ")
            payment_method = input("Payment Method: ")
            shipping_time_days = int(input("Shipping Time (days): "))
            location = input("Location: ")
            device = input("Device: ")
            delivery_status = input("Delivery Status: ")
            is_returned = input("Returned (True/False): ").lower() == "true"

            create_order(
                user_id,
                product_id,
                purchase_date,
                payment_method,
                shipping_time_days,
                location,
                device,
                delivery_status,
                is_returned,
            )

        elif choice == "5":
            break

        else:
            print("Invalid Choice")


def read_menu():
    while True:
        print("\n========== READ MENU ==========")
        print("1. Get User")
        print("2. Get Product")
        print("3. Get Seller")
        print("4. View All Users")
        print("5. View All Products")
        print("6. View All Sellers")
        print("7. View All Orders")
        print("8. Back")

        choice = input("Enter choice: ")

        if choice == "1":
            print(get_user(input("User ID: ")))

        elif choice == "2":
            print(get_product(input("Product ID: ")))

        elif choice == "3":
            print(get_seller(input("Seller ID: ")))

        elif choice == "4":
            for i in get_all_users():
                print(i)

        elif choice == "5":
            for i in get_all_products():
                print(i)

        elif choice == "6":
            for i in get_all_sellers():
                print(i)

        elif choice == "7":
            for i in get_all_orders():
                print(i)

        elif choice == "8":
            break

        else:
            print("Invalid Choice")


def update_menu():
    while True:
        print("\n========== UPDATE MENU ==========")
        print("1. Update Product Price")
        print("2. Update Product Stock")
        print("3. Update Product Rating")
        print("4. Update Seller Rating")
        print("5. Update Delivery Status")
        print("6. Back")

        choice = input("Enter choice: ")

        if choice == "1":
            update_product_price(
                input("Product ID: "),
                float(input("New Price: "))
            )

        elif choice == "2":
            update_product_stock(
                input("Product ID: "),
                int(input("New Stock: "))
            )

        elif choice == "3":
            update_product_rating(
                input("Product ID: "),
                float(input("New Rating: "))
            )

        elif choice == "4":
            update_seller_rating(
                input("Seller ID: "),
                float(input("New Rating: "))
            )

        elif choice == "5":
            update_delivery_status(
                input("User ID: "),
                input("Product ID: "),
                input("New Delivery Status: ")
            )

        elif choice == "6":
            break

        else:
            print("Invalid Choice")


def delete_menu():
    while True:
        print("\n========== DELETE MENU ==========")
        print("1. Delete User")
        print("2. Delete Product")
        print("3. Delete Seller")
        print("4. Delete Order")
        print("5. Back")

        choice = input("Enter choice: ")

        if choice == "1":
            _report(delete_user(input("User ID: ")), "User")

        elif choice == "2":
            _report(delete_product(input("Product ID: ")), "Product")

        elif choice == "3":
            _report(delete_seller(input("Seller ID: ")), "Seller")

        elif choice == "4":
            _report(
                delete_order(input("User ID: "), input("Product ID: ")),
                "Order"
            )

        elif choice == "5":
            break

        else:
            print("Invalid Choice")


def main():
    while True:
        print("\n====================================")
        print(" AMAZON E-COMMERCE MANAGEMENT SYSTEM")
        print("====================================")
        print("1. Create")
        print("2. Read")
        print("3. Update")
        print("4. Delete")
        print("5. Search & Filter")
        print("6. Exit")

        choice = input("Enter choice: ")

        if choice == "1":
            _safe(create_menu)

        elif choice == "2":
            _safe(read_menu)

        elif choice == "3":
            _safe(update_menu)

        elif choice == "4":
            _safe(delete_menu)

        elif choice == "5":
            search_menu()

        elif choice == "6":
            print("Thank You!")
            break

        else:
            print("Invalid Choice")


if __name__ == "__main__":
    main()