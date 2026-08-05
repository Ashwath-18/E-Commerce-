"""
Cartify Database Initialization Script

This script performs the following steps:
1. Creates all MongoDB collections (if they don't already exist)
2. Creates indexes on important fields
3. Imports the dataset into the database

Run:
    python database/initialize_database.py
"""
from database.create_collections import create_collections
from database.create_indexes import create_indexes
from database.import_data import import_dataset
from config.mongodb import db

if db["Orders"].count_documents({}) > 0:
    print("⚠️ Database already initialized.")
    print("Run app.py instead.")
    exit()

def initialize_database():

    print("=" * 60)
    print(" CARTIFY DATABASE INITIALIZATION ")
    print("=" * 60)

    create_collections()

    print()

    create_indexes()

    print()

    import_dataset()

    print()

    print("🎉 Cartify Database Ready")


if __name__ == "__main__":
    initialize_database()