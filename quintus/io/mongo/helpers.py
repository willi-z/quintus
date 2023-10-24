from typing import Type
from pydantic import BaseModel


def generate_attr_filter(model: Type[BaseModel], usage: str | None = None) -> dict:
    fields = model.__fields__
    attr_filter = []
    if usage is not None:
        attr_filter.append({"usage": {"$in": [usage]}})
    for attr, field in fields.items():
        if not field.required:
            continue
        attr_filter.append({attr: {"$exists": True}})

    return {"$and": attr_filter}


def filter_db_entires(db, usage: str, attributes: set[str]):
    query = [{"usage": {"$in": [usage]}}]

    for attr in attributes:
        query.append({attr: {"$exists": True}})

    final_query = {"$and": query}
    # print(final_query)
    findings = db.find(final_query)
    return findings
