from abc import ABC, abstractmethod
from quintus.io import DataSet, DataWriter
from quintus.evals import Evaluation
from quintus.evals.helpers import validate_evaluations


class DataWalker(ABC):
    @abstractmethod
    def walk(self):
        pass


class BasicDataWalker(DataWalker):
    def __init__(
        self, dataset: DataSet, evaluations: set[Evaluation], writer: DataWriter
    ):
        validate_evaluations(evaluations)

        self.dataset = dataset
        self.evaluations = evaluations
        self.writer = writer
