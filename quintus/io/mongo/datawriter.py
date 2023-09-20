from quintus.io.datawriter import DataWriter
from typing import Iterator
import pymongo


class MongoDataWriter(DataWriter):
    def __init__(
        self,
        host="localhost",
        port=27017,
        databas="quintus",
        document="materials",
        override=True,
    ) -> None:
        self.client = pymongo.MongoClient(host, port)
        self.db = self.client[databas]
        self.document = self.db[document]
        if override:
            self.document.drop()

    def write_entry(self, entry: dict, filter: dict = None):
        if filter is None:
            self.document.insert_one(entry)
        else:
            self.document.update_one(filter, {"$set": entry})

    def get_entry(self, id: str) -> Iterator[dict]:
        return self.document.find({"_id": id})
