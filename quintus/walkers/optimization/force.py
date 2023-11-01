from quintus.helpers.id_generation import generate_id
from quintus.structures.component import Component
from .optimizer import Optimizer
import warnings


def calc_config_indeces(index: int, sizes: list[int]) -> list[int]:
    """_summary_

    Parameters
    ----------
    index : int
        _description_
    sizes : list[int]
        _description_

    Returns
    -------
    list[int]
        _description_
    """
    indeces = [0] * len(sizes)
    digit = 0
    while index > 0:
        rest = int(index % sizes[digit])
        indeces[digit] = rest
        index -= rest
        index = int(index / sizes[digit])
        digit += 1
    return indeces


class BruteForceOptimizer(Optimizer):
    def walk(self):
        sizes = [1] * len(self.subsets)
        total_combinations = 1
        iters = dict[str, list[dict]]()
        index = 0
        for key, dataset in self.subsets.items():
            sizes[index] = len(dataset)
            if sizes[index] == 0:
                warnings.warn(
                    f"No match found for reqired attribute: '{key}'!", UserWarning
                )
            total_combinations *= sizes[index]
            iters[key] = list(dataset.find())
            index += 1

        if total_combinations == 0:
            warnings.warn("Found no possible combinations!", UserWarning)

        keys = list[str](iters.keys())
        values = list[list[dict]](iters.values())

        def get_config(index: int) -> dict[str, dict]:
            indeces = calc_config_indeces(index, sizes)

            config_values = list[dict]()
            for i in range(len(values)):
                index = indeces[i]
                value = values[i]
                config_values.append(value[index])

            config = dict[str, dict]()
            for i in range(len(keys)):
                config.update({keys[i]: config_values[i]})
            return config

        print(end="")
        for i in range(total_combinations):
            config = get_config(i)
            entry = Component(identifier=generate_id())
            entry.composition = config
            entry.properties = dict()
            for evaluation in self.evaluations:
                entry.properties.update(evaluation.evaluate(**config))

            self.writer.write_entry(entry)
            print(
                "\r" + f"BruteForceOptimizer: ({i + 1} / {total_combinations})", end=""
            )
        print("...completed!")
