from quintus.evals import BasicEvaluation
from typing import Type
from quintus.structures import Measurements, generate_attr_filter


def validate_battery_filters(filters: dict[str, dict], raise_error=True) -> bool:
    args = list(filters.keys())
    keys = ["anode", "cathode", "foil", "separator"]
    for arg in args:
        if arg not in keys:
            if raise_error:
                raise KeyError(f'"{arg}" is not part of required keys: {keys}.')
            return False
    return True


class BatteryEvaluation(BasicEvaluation):
    def __init__(
        self,
        name: str,
        unit: str | None,
        filters: dict[str, dict] | None,
        validate_filters=True,
    ):
        if validate_filters:
            validate_battery_filters(filters)
        super().__init__(name, unit, filters)


class FastBatterEvaluation(BatteryEvaluation):
    def __init__(
        self,
        name: str,
        unit: str | None,
        eval_args: dict[str, Type[Measurements]],
        req_usage: dict[str, str] = None,
    ):
        filters = dict()
        if req_usage is None:
            req_usage = dict()
        for arg, arg_type in eval_args.items():
            filters[arg] = generate_attr_filter(arg_type, req_usage.get(arg))
        super().__init__(name, unit, filters)
