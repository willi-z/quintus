from abc import ABC, abstractmethod
from quintus.structures import Measurement
from quintus.helpers import parse_unit


class Evaluation(ABC):
    @abstractmethod
    def get_result_names(self) -> set[str]:
        pass

    @abstractmethod
    def filter_per_args(self) -> dict[str, dict]:
        pass

    @abstractmethod
    def evaluate(self, **kwargs) -> dict[str, dict]:
        pass


def validate_kwargs(filters: dict[str, dict], raise_error=True, **kwargs) -> bool:
    args = list(kwargs.keys())
    keys = list(filters.keys())

    for key in keys:
        if key not in args:
            if raise_error:
                raise AttributeError(f'"{key}" is not in provided arguments: {args}.')
            return False
    return True


class BasicEvaluation(Evaluation):
    def __init__(
        self,
        name: str,
        unit: str | None,
        filters: dict[str, dict] | None,
    ):
        """Searches for a component with the help of a filter,
        then computes one property and returns the property value with
        a certain unit.

        Parameters
        ----------
        name : str
            name of the property
        unit : str | None
            unit of the property
        filters : dict[str, dict] | None
            search filter for vaible components
        """
        self.name = name
        self.unit = unit
        self.filters = filters

    @abstractmethod
    def __compute__(self, **kwargs) -> float:
        """Override the method to describe the evaluation computation.
        Don't call this method directly!
        It is meant to be called by evalute().

        Returns
        -------
        float
            value in SI units, the conversion to the
            given unit is done when it is called by evaluate!
        """
        pass

    def get_result_names(self) -> set[str]:
        """_summary_

        Returns
        -------
        set[str]
            _description_
        """
        return {self.name}

    def filter_per_args(self) -> dict[str, dict]:
        """Filter per argument requred by the evaluation compute function.

        Returns
        -------
        dict[str, dict]
            _description_
        """
        return self.filters

    def evaluate(self, **kwargs) -> dict[str, Measurement]:
        """_summary_

        Returns
        -------
        dict[str, dict]
            _description_
        """
        validate_kwargs(self.filter_per_args(), True, **kwargs)
        measurement = Measurement(
            value=self.__compute__(**kwargs) / parse_unit(self.unit),
            unit=self.unit,
            source="computation",
        )
        return {self.name: measurement}
