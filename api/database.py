import os

from pymongo import MongoClient

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DATABASE = os.getenv("MONGO_DATABASE", "techtudo")

client = MongoClient(MONGO_URI)
db = client[MONGO_DATABASE]


def get_collection():
    return db["noticias"]
