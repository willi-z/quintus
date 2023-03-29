from abc import ABC, abstractmethod
from quintus.structures import Measurement


class Evaluation(ABC):
    @abstractmethod
    def get_result_name(self) -> str:
        pass

    @abstractmethod
    def filter_per_args(self) -> dict[str, dict]:
        pass

    @abstractmethod
    def evaluate(self, **kwargs) -> dict[str, Measurement]:
        pass


def validate_kwargs(filters: dict[str, dict], raise_error=True, **kwargs) -> bool:
    args = list(kwargs.keys())
    keys = list(filters.keys())

    for key in keys:
        if key not in args:
            if raise_error:
                raise KeyError(f'"{key}" is not in provided arguments: {args}.')
            return False
    return True


class BasicEvaluation(Evaluation):
    def __init__(
        self,
        name: str,
        unit: str | None,
        filters: dict[str, dict] | None,
    ):
        self.name = name
        self.unit = unit
        self.filters = filters

    @abstractmethod
    def compute(self, **kwargs) -> float:
        pass

    def get_result_name(self) -> str:
        return self.name

    def filter_per_args(self) -> dict[str, dict]:
        return self.filters

    def evaluate(self, **kwargs) -> dict[str, Measurement]:
        validate_kwargs(self.filter_per_args(), True, **kwargs)
        measurement = Measurement(
            value=self.compute(**kwargs), unit=self.unit, source="computation"
        )
        return {self.get_result_name(): measurement}
