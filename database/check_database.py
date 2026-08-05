from database.helpers import *

print(users.count_documents({}))
print(products.count_documents({}))
print(orders.count_documents({}))