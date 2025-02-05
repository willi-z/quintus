from abc import ABC, abstractmethod
from quintus.structures import Measurement, Component
from quintus.helpers import parse_unit


class Evaluation(ABC):
    @abstractmethod
    def get_result_names(self) -> set[str]:
        """Returns the names of all results generated.
        Usefull when trying to figure out cross dependecies
        without the need for computing the evaluation.

        Returns
        -------
        set[str]
            the names/keys of all computed results
            provided by the evaluate() function
            (the "set" prevents the usage the same names)
        """
        pass

    @abstractmethod
    def get_required_names(self) -> set[str]:
        """Filter per argument requred by the evaluation compute function.

        Returns
        -------
        dict[str, dict]
            key is the argument needed during computation.
            dict is filter using the query system from MongoDB
            (see: https://www.mongodb.com/docs/manual/tutorial/query-documents/)
        """
        pass

    @abstractmethod
    def filter_per_component(self) -> dict[str, dict]:
        """Filter per argument requred by the evaluation compute function.

        Returns
        -------
        dict[str, dict]
            key is the argument needed during computation.
            dict is filter using the query system from MongoDB
            (see: https://www.mongodb.com/docs/manual/tutorial/query-documents/)
        """
        pass

    @abstractmethod
    def evaluate(self, **kwargs) -> dict[str, dict]:
        pass


def validate_kwargs(filters: dict[str, dict], raise_error=True, **kwargs) -> bool:
    """
    """
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
        required_measurements: set[str] | None,
        component_filters: dict[str, dict] | None,
    ):
        """Searches for a component with the help of a filter,
        then computes a single property and returns the property value with
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
        self.required_measurements = required_measurements
        self.component_filters = component_filters

    @abstractmethod
    def __compute__(self, component: Component) -> float:
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
        """Returns the names of all results generated.
        Usefull when trying to figure out cross dependecies
        without the need for computing the evaluation.
        Returns
        -------
        set[str]
            the names/keys of all computed results
            provided by the evaluate() function
            (the "set" prevents the usage the same names)
        """
        return {self.name}
    
    def get_required_names(self) -> set[str]:
        """Filter per argument requred by the evaluation compute function.

        Returns
        -------
        set[str]
            key is the measuremnt needed during computation.
        """
        if self.required_measurements is None:
            return set[str]()
        return self.required_measurements

    def filter_per_component(self) -> dict[str, dict]:
        """Filter per argument requred by the evaluation compute function.

        Returns
        -------
        dict[str, dict]
            key is the argument needed during computation.
            dict is filter using the query system from MongoDB
            (see: https://www.mongodb.com/docs/manual/tutorial/query-documents/)
        """
        return self.component_filters

    def evaluate(self, component: Component) -> dict[str, Measurement]:
        """main function to call when runing the

        Returns
        -------
        dict[str, dict]
            keys are the same as given by get_results_names()
            Values are the results
        """
        # validate_kwargs(self.filter_per_args(), True, **kwargs)
        measurement = Measurement(
            value=self.__compute__(component) / parse_unit(self.unit),
            unit=self.unit,
            source="computation",
        )
        return {self.name: measurement}
