from quintus.io.datawriter import DataWriter
from quintus.structures import Component
import pymongo


class MongoDataWriter(DataWriter):
    def __init__(
        self,
        host="localhost",
        port=27017,
        database="quintus",
        document="materials",
        override=True,
    ) -> None:
        self.client = pymongo.MongoClient(host, port)
        self.db = self.client[database]
        self.document = self.db[document]
        if override:
            self.document.drop()

    def write_entry(self, entry: Component, override=True):
        content = entry.dict(exclude_unset=True, exclude_none=True)
        if override is True:
            self.document.insert_one(content)
        else:
            self.document.update_one({"_id": entry._id}, content, upsert=True)
