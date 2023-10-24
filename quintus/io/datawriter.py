from abc import ABC, abstractmethod
from quintus.structures import Component


class DataWriter(ABC):
    @abstractmethod
    def write_entry(self, entry: Component, override=True) -> None:
        pass
