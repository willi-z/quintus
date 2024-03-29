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
        username: str = None,
        password: str = None,
        init_filter: dict | None = None,
    ) -> None:
        self.host_name = host
        self.port = port
        self.database_name = database
        self.document_name = document
        self.username = username
        self.password = password

        self.client = pymongo.MongoClient(
            host, port, username=username, password=password
        )
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
            host=self.host_name,
            port=self.port,
            database=self.database_name,
            document=self.document_name,
            username=self.username,
            password=self.password,
            init_filter=final_filter,
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
