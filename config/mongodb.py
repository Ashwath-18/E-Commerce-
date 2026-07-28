from pymongo import MongoClient

# Connect to MongoDB Server
client = MongoClient("mongodb://localhost:27017/")

# Create / Connect to Database
db = client["AmazonDB"]

print("Connected to MongoDB Successfully!")
