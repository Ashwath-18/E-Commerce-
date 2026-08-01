"""
Search and Filter Menu
"""

from search.search_products import *
from search.filter_products import *


def search_menu():

    while True:

        print("\n========== SEARCH & FILTER MENU ==========")
        print("1. Search Product by ID")
        print("2. Search Products by Brand")
        print("3. Search Products by Category")
        print("4. Search Products by Subcategory")
        print("5. Search Products by Price Range")
        print("6. Search Products by Rating")
        print("7. Filter Products by Rating")
        print("8. Filter Products by Price Range")
        print("9. Filter In Stock Products")
        print("10. Filter Returned Orders")
        print("11. Filter Delivered Orders")
        print("12. Filter Orders by Payment Method")
        print("13. Exit")

        choice = input("\nEnter your choice: ")

        if choice == "1":

            product_id = input("Enter Product ID: ")
            result = search_product_by_id(product_id)

            if result:
                print(result)
            else:
                print("Product not found.")

        elif choice == "2":

            brand = input("Enter Brand: ")
            result = search_products_by_brand(brand)

            if result:
                for product in result:
                    print(product)
            else:
                print("No products found.")

        elif choice == "3":

            category = input("Enter Category: ")
            result = search_products_by_category(category)

            if result:
                for product in result:
                    print(product)
            else:
                print("No products found.")

        elif choice == "4":

            subcategory = input("Enter Subcategory: ")
            result = search_products_by_subcategory(subcategory)

            if result:
                for product in result:
                    print(product)
            else:
                print("No products found.")

        elif choice == "5":

            min_price = float(input("Enter Minimum Price: "))
            max_price = float(input("Enter Maximum Price: "))

            result = search_products_by_price_range(min_price, max_price)

            if result:
                for product in result:
                    print(product)
            else:
                print("No products found.")

        elif choice == "6":

            rating = float(input("Enter Minimum Rating: "))

            result = search_products_by_rating(rating)

            if result:
                for product in result:
                    print(product)
            else:
                print("No products found.")

        elif choice == "7":

            rating = float(input("Enter Minimum Rating: "))

            result = filter_products_by_rating(rating)

            if result:
                for product in result:
                    print(product)
            else:
                print("No products found.")

        elif choice == "8":

            min_price = float(input("Enter Minimum Price: "))
            max_price = float(input("Enter Maximum Price: "))

            result = filter_products_by_price(min_price, max_price)

            if result:
                for product in result:
                    print(product)
            else:
                print("No products found.")

        elif choice == "9":

            result = filter_products_in_stock()

            if result:
                for product in result:
                    print(product)
            else:
                print("No products found.")

        elif choice == "10":

            result = filter_returned_orders()

            if result:
                for order in result:
                    print(order)
            else:
                print("No returned orders found.")

        elif choice == "11":

            result = filter_delivered_orders()

            if result:
                for order in result:
                    print(order)
            else:
                print("No delivered orders found.")

        elif choice == "12":

            payment = input("Enter Payment Method: ")

            result = filter_orders_by_payment(payment)

            if result:
                for order in result:
                    print(order)
            else:
                print("No orders found.")

        elif choice == "13":

            print("Exiting Search Menu...")
            break

        else:

            print("Invalid Choice. Please try again.")