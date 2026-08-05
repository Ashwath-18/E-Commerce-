from pymongo import MongoClient

# Connect to MongoDB Server
client = MongoClient("mongodb://localhost:27017/")

# Create / Connect to Database
db = client["CartifyDB"]

if __name__ == "__main__":
    print("Connected to MongoDB Successfully!")