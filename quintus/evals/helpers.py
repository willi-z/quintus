from .evaluation import Evaluation
from typing import cast


def generate_filters(evaluations: list[Evaluation]) -> dict[str, dict]:
    filters = dict[str, dict]()
    for evaluation in evaluations:
        eval_filter = evaluation.filter_per_args()
        for key, filter in eval_filter.items():
            if filters.get(key) is None:
                filters[key] = {"$and": []}  # {"usage": {"$in": [key]}}

            filter_list = cast(list, filters[key]["$and"])
            filter_list.append(filter)

    return filters
