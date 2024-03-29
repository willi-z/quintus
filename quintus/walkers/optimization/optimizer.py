from quintus.walkers import BasicDataWalker
from quintus.io import DataSet, DataWriter
from quintus.evals import Evaluation, generate_filters
from pprint import pprint


class Optimizer(BasicDataWalker):
    def __init__(
        self,
        dataset: DataSet,
        evaluations: set[Evaluation],
        writer: DataWriter,
    ):
        super().__init__(dataset, evaluations, writer)
        self.subsets = dict[str, DataSet]()
        filters = generate_filters(evaluations)
        for key, filter in filters.items():
            self.subsets[key] = self.dataset.reduce_set(filter)
            print(f"For dataset {key} found {len(self.subsets[key])} entires.")
            pprint(filter)
            results = self.subsets[key].find()
            for res in results:
                print(res["name"])

    def walk(self):
        for key, dataset in self.subsets.items():
            print(f"for {key} found:")
            results = dataset.find()
            for res in results:
                print(res["name"])
            print("##################")
