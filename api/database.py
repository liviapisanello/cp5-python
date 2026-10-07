import os
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient

# Carrega o .env da raiz do projeto (dois níveis acima de api/)
load_dotenv(Path(__file__).parent.parent / ".env")

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27019")
MONGO_DATABASE = os.getenv("MONGO_DATABASE", "books_db")

client = MongoClient(MONGO_URI)
db = client[MONGO_DATABASE]


def get_db():
    return db
