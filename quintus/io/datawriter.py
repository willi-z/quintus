from abc import ABC, abstractmethod


class DataWriter(ABC):
    @abstractmethod
    def write_entry(self, entry: dict) -> None:
        pass
