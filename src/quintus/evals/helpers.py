from .evaluation import Evaluation


def generate_filters(evaluations: list[Evaluation]) -> dict[str, dict]:
    filters = dict[str, dict]()
    for evaluation in evaluations:
        eval_filter = evaluation.filter_per_component()
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
    """
    Check that no two evaluations gernate the same result.
    """
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


def sort_evaluations(
    evaluations: list[Evaluation] | set[Evaluation], raise_error=True
) -> list[Evaluation]:
    evaluation_order = list[Evaluation]()
    for evaluation in evaluations:
        inputs = evaluation.get_required_names()
        outputs = evaluation.get_result_names()
        is_inserted = False
        for i in range(len(evaluation_order)):
            exisiting = evaluation_order[i]
            if len(exisiting.get_required_names().intersection(outputs)) >= 1:
                evaluation_order.insert(i, evaluation)
                is_inserted = True
                break
            if len(inputs) < len(exisiting.get_required_names()):
                evaluation_order.insert(i, evaluation)
                is_inserted = True
                break
        if not is_inserted:
            evaluation_order.append(evaluation)

    if raise_error:
        results = set[str]()
        for evaluation in evaluation_order:
            missing_requirements = evaluation.get_required_names() - results
            if len(missing_requirements) != 0:
                raise KeyError(f"'{evaluation}' requires {missing_requirements} that are not provided previously!")
            results = results | evaluation.get_result_names() # union
    return evaluation_order
