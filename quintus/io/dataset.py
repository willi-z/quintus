from abc import ABCMeta, abstractmethod
from typing import Iterator


class DataSet(metaclass=ABCMeta):
    @abstractmethod
    def __len__(self) -> int:
        pass

    @abstractmethod
    def reduce_set(self, filter: dict) -> "DataSet":
        pass

    @abstractmethod
    def find(self, query: dict | None) -> Iterator[dict]:
        pass
