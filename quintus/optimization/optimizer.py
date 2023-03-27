from quintus.io import DataSet, DataWriter
from quintus.evals import Evaluation


class Optimizer:
    dataset: DataSet

    def __init__(
        self, dataset: DataSet, evaluations: set[Evaluation], writer: DataWriter
    ):
        pass

    def set_dataset(dataset: DataSet):
        pass

    def register_evaluation(evaluations: set[Evaluation]):
        pass

    def set_output(writer: DataWriter):
        pass
