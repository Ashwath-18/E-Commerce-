from pymongo import MongoClient

# Connect to MongoDB Server (fail fast if the server is not running)
client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)

# Create / Connect to Database
db = client["CartifyDB"]

if __name__ == "__main__":
    print("Connected to MongoDB Successfully!")