from pydantic import BaseModel
from pymongo.database import Database


def collect_model_attr(models: list[BaseModel]):
    fields = set()
    for model in models:
        attr = model.__fields__.keys()
        fields.update(attr)
    return fields


def filter_db_entires(db: Database, usage: str, attributes: set[str]):
    query = [{"usage": {"$in": [usage]}}]

    for attr in attributes:
        query.append({attr: {"$exists": True}})

    final_query = {"$and": query}
    # print(final_query)
    findings = db.find(final_query)
    return findings
