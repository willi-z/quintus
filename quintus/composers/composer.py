from quintus.structures import Component, Composition
from abc import abstractmethod, ABC

class Composer(ABC):
    @abstractmethod
    def generate(self, components: dict[str, Component]) -> Composition:
        pass

    def is_compatible_with(self, component_key: str) -> bool:
        return True