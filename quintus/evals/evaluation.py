from abc import ABC, abstractmethod


class Evaluation(ABC):
    @abstractmethod
    def get_required_attrs(self) -> dict[str, set[str]]:
        pass

    @abstractmethod
    def evaluate(self, **kwargs) -> float:
        pass
