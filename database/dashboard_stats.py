from database.helpers import (
    products,
    users,
    orders,
    reviews
)


def total_products():
    return products.count_documents({})


def total_users():
    return users.count_documents({})


def total_orders():
    return orders.count_documents({})


def total_reviews():
    return reviews.count_documents({})