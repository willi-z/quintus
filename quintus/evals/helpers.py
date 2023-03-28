from .evaluation import Evaluation
from typing import cast


def collect_required_attr(evaluations: list[Evaluation]) -> dict[set[str]]:
    result = dict[str, set[str]]()
    for eval in evaluations:
        for key, attrs in eval.get_required_attrs().items():
            if result.get(key) is None:
                result[key] = attrs
            else:
                result[key].update(attrs)
    return result


def generate_filters(required_attr: dict[set[str]]) -> dict[dict]:
    filters = dict[str, dict]()
    for key, attrs in required_attr.items():
        if filters.get(key) is None:
            filters[key] = {"$and": [{"usage": {"$in": [key]}}]}

        filter = cast(list, filters[key]["$and"])
        for attr in attrs:
            filter.append({attr: {"$exists": True}})

    return filters
