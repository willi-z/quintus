from quintus.io.dataset import DataSet
from typing import Iterator
import pymongo


class MongoDataSet(DataSet):
    def __init__(
        self,
        host="localhost",
        port=27017,
        database="quintus",
        document="materials",
        init_filter: dict | None = None,
    ) -> None:
        self.host_name = host
        self.port = port
        self.database_name = database
        self.document_name = document

        self.client = pymongo.MongoClient(host, port)
        self.db = self.client[database]
        self.document = self.db[document]
        self.filter = init_filter
        self.size = 0
        if self.filter is None:
            self.size = self.document.count_documents(dict())
        else:
            self.size = self.document.count_documents(self.filter)

    def __len__(self) -> int:
        return self.size

    def reduce_set(self, filter: dict) -> DataSet:
        final_filter = None
        if filter is not None and self.filter is not None:
            final_filter = {"$and": [self.filter, filter]}
        elif filter is not None:
            final_filter = filter
        elif self.filter is not None:
            final_filter = self.filter

        return MongoDataSet(
            self.host_name,
            self.port,
            self.database_name,
            self.document_name,
            final_filter,
        )

    def find(self, query: dict | None = None) -> Iterator[dict]:
        final_query = None
        if query is not None and self.filter is not None:
            final_query = {"$and": [self.filter, query]}
        elif query is not None:
            final_query = query
        elif self.filter is not None:
            final_query = self.filter

        return self.document.find(final_query)
