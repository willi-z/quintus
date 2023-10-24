def filter_db_entires(db, usage: str, attributes: set[str]):
    query = [{"usage": {"$in": [usage]}}]

    for attr in attributes:
        query.append({attr: {"$exists": True}})

    final_query = {"$and": query}
    # print(final_query)
    findings = db.find(final_query)
    return findings
