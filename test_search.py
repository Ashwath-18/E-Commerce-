from search.search_products import *

print("\n----- Search Product by ID -----")
print(search_product_by_id("P000001"))

print("\n----- Search by Brand -----")
print(search_products_by_brand("Samsung"))

print("\n----- Search by Category -----")
print(search_products_by_category("Electronics"))

print("\n----- Search by Subcategory -----")
print(search_products_by_subcategory("Mobile"))

print("\n----- Search by Price Range -----")
print(search_products_by_price_range(500, 1000))

print("\n----- Search by Rating -----")
print(search_products_by_rating(4.5))

print("\n----- Search Orders by User -----")
print(search_orders_by_user("U000001"))

print("\n----- Search Sellers by Rating -----")
print(search_sellers_by_rating(4.5))