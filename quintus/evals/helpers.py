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


def validate_evaluations(
    evaluations: list[Evaluation] | set[Evaluation], raise_error=True
) -> bool:
    keys = set()
    for evaluation in evaluations:
        key = evaluation.get_result_name()
        if key in keys:
            if raise_error:
                raise KeyError(f"'{key}' is already used!")
            return False
    return True
