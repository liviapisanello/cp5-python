import os
from pymongo import MongoClient, UpdateOne
from itemadapter import ItemAdapter

class MongoPipeline:
    def open_spider(self, spider):
        uri = os.getenv("MONGO_URI", "mongodb://localhost:27019")
        db_name = spider.settings.get("MONGO_DATABASE", "books_db")
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.collection = self.db["livros"]
        self.collection.create_index("upc", unique=True)

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        doc = dict(adapter)
        upc = doc.get("upc", "")
        if upc:
            self.collection.update_one(
                {"upc": upc},
                {"$set": doc},
                upsert=True
            )
        else:
            self.collection.insert_one(doc)
        return item
