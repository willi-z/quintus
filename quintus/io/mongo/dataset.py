from quintus.io.dataset import DataSet
import pymongo
from .filter import collect_model_attr, filter_db_entires


class MongoDataSet(DataSet):
    def __init__(
        self, host="localhost", port=27017, databas="quintus", document="materials"
    ) -> None:
        self.client = pymongo.MongoClient(host, port)
        self.db = self.client[databas]
        self.document = self.db[document]

    def reduce_set(self, usages: dict):
        for key, types in usages.items():
            attrs = collect_model_attr(types)
            # print(attrs)
            results = filter_db_entires(self.document, key, attrs)
            for result in results:
                print(result["name"])
