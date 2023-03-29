from quintus.io import DataSet, DataWriter
from quintus.evals import Evaluation, generate_filters


class Optimizer:
    def __init__(
        self,
        dataset: DataSet,
        evaluations: set[Evaluation],
        writer: DataWriter,
        combined_search=True,
    ):
        self.evaluations = evaluations
        self.writer = writer

        filters = generate_filters(evaluations)
        self.dataset = dataset
        self.subsets = dict[str, DataSet]()

        for key, filter in filters.items():
            self.subsets[key] = self.dataset.reduce_set(filter)

    def search(self):
        for key, dataset in self.subsets.items():
            print(f"for {key} found:")
            results = dataset.find()
            for res in results:
                print(res["name"])
            print("##################")
