from quintus.io.datawriter import DataWriter
from quintus.structures import Component
import pymongo

from quintus.structures.helpers import component_to_dict


class MongoDataWriter(DataWriter):
    def __init__(
        self,
        host="localhost",
        port=27017,
        database="quintus",
        document="materials",
        override=True,
        username: str = None,
        password: str = None,
    ) -> None:
        self.client = pymongo.MongoClient(
            host, port, username=username, password=password
        )
        self.db = self.client[database]
        self.document = self.db[document]
        if override:
            self.document.drop()

    def write_entry(self, entry: Component, override=True):
        content = component_to_dict(entry)
        if override is True:
            self.document.insert_one(content)
        else:
            self.document.update_one({"_id": content.get("_id")}, content, upsert=True)
