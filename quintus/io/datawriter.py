from abc import ABC, abstractmethod


class DataWriter(ABC):
    @abstractmethod
    def write_entry(self, entry: dict, filter: dict = None) -> None:
        pass
