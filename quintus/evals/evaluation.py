from abc import ABC, abstractmethod
from quintus.structures import Measurement


class Evaluation(ABC):
    @abstractmethod
    def filter_per_args(self) -> dict[str, dict]:
        pass

    @abstractmethod
    def evaluate(self, **kwargs) -> dict[str, Measurement]:
        pass
