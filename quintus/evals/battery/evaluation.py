from quintus.evals import Evaluation
from typing import Type
from abc import abstractmethod
from quintus.structures import Measurement, Measurements, generate_attr_filter


def validate_battery_filters(filters: dict[str, dict], raise_error=True) -> bool:
    args = list(filters.keys())
    keys = ["anode", "cathode", "foil", "separator"]
    for arg in args:
        if arg not in keys:
            if raise_error:
                raise KeyError(f'"{arg}" is not part of required keys: {keys}.')
            return False
    return True


def validate_battery_kwargs(
    filters: dict[str, dict], raise_error=True, **kwargs
) -> bool:
    args = list(kwargs.keys())
    keys = list(filters.keys())

    for key in keys:
        if key not in args:
            if raise_error:
                raise KeyError(f'"{key}" is not in provided arguments: {args}.')
            return False
    return True


class BatteryEvaluation(Evaluation):
    def __init__(
        self,
        name: str,
        unit: str | None,
        filters: dict[str, dict] | None,
        validate_filters=True,
    ):
        self.name = name
        self.unit = unit
        if validate_filters:
            validate_battery_filters(filters)
        self.filters = filters

    def filter_per_args(self) -> dict[str, dict]:
        return self.filters

    @abstractmethod
    def compute(self, **kwargs) -> float:
        pass

    def evaluate(self, **kwargs) -> dict[str, Measurement]:
        validate_battery_kwargs(self.filters, kwargs=kwargs)
        measurement = Measurement(
            value=self.compute(kwargs), unit=self.unit, source="computation"
        )
        return {self.name: measurement}


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
