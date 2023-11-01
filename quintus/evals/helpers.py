from .evaluation import Evaluation


def generate_filters(evaluations: list[Evaluation]) -> dict[str, dict]:
    filters = dict[str, dict]()
    for evaluation in evaluations:
        eval_filter = evaluation.filter_per_args()
        for key, filter in eval_filter.items():
            if filter is None:
                continue
            if filters.get(key) is None:
                filters[key] = dict()
            filters[key].update(filter)
    return filters


def validate_evaluations(
    evaluations: list[Evaluation] | set[Evaluation], raise_error=True
) -> bool:
    keys = set[str]()
    for evaluation in evaluations:
        new_keys = evaluation.get_result_names()
        duplicate_keys = keys & new_keys  # intersection
        if len(duplicate_keys) != 0:
            if raise_error:
                raise KeyError(f"'{duplicate_keys}' already used!")
            return False
        keys.update(new_keys)
    return True
