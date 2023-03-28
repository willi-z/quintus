from quintus.io import DataSet, DataWriter
from quintus.evals import Evaluation, collect_required_attr, generate_filters


class Optimizer:
    def __init__(
        self, dataset: DataSet, evaluations: set[Evaluation], writer: DataWriter
    ):
        self.evaluations = evaluations
        self.writer = writer

        requirements = collect_required_attr(evaluations)
        filters = generate_filters(requirements)
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
