from abc import ABC, abstractmethod
from typing import Type
from quintus.structures import Measurements


class Evaluation(ABC):
    @abstractmethod
    def get_args_form(self) -> dict[str, Type[Measurements]]:
        pass

    @abstractmethod
    def evaluate(self, **kwargs) -> float:
        pass
