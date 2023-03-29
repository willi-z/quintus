from quintus.io.datawriter import DataWriter
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
