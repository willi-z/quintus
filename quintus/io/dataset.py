from abc import ABCMeta, abstractmethod


class DataSet(metaclass=ABCMeta):
    @abstractmethod
    def reduce_set(self, usages: dict):  # : dict[set[Type(Measurements)]]
        pass

    # @abstractmethod
    # def find_closest(self, reference: Measurements) -> Measurements:
    #     pass
