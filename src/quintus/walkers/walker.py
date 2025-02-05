from abc import ABC, abstractmethod
from quintus.io import DataSet, DataWriter
from quintus.composers import Composer
from quintus.evals import Evaluation
from quintus.evals.helpers import validate_evaluations, sort_evaluations


class DataWalker(ABC):
    @abstractmethod
    def walk(self):
        pass


class BasicDataWalker(DataWalker):
    def __init__(
        self, dataset: DataSet, composer: Composer, evaluations: set[Evaluation], writer: DataWriter
    ):
        validate_evaluations(evaluations)

        self.dataset = dataset
        self.composer = composer
        self.evaluations = sort_evaluations(evaluations)
        self.writer = writer
