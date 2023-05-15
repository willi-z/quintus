from my_secret_path import mypath  # str of directory

from quintus.io.excel import ExcelReader
from quintus.io.mongo import MongoDataWriter, MongoDataSet  # noqa

from quintus.evals.battery.component import ElectrodeCapacityCalc

from quintus.evals.battery import (
    CapacityEvaluation,  # noqa
    StiffnessEvaluation,
    EnergyDensity,
)

from quintus.walkers import DataFiller
from quintus.walkers.optimization import BruteForceOptimizer

writer = MongoDataWriter()

ExcelReader(
    mypath + "quintus_data_v1.0.0.xlsx", mypath + "config_v1.0.0.json", writer
).read_all()


def data_extension():
    # Componentwise Dateset-Extension
    evaluations = set()
    evaluations.add(ElectrodeCapacityCalc())
    dataset = MongoDataSet()
    result_writer = MongoDataWriter(override=False)  # same set!
    optimizer = DataFiller(dataset, evaluations, result_writer)
    optimizer.walk()


# data_extension()


def stage1_evaluation():
    # first simple evaluation
    evaluations = set()
    # evaluations.add(CapacityEvaluation())
    evaluations.add(StiffnessEvaluation())
    evaluations.add(EnergyDensity())

    dataset = MongoDataSet()
    result_writer = MongoDataWriter(document="results1")

    optimizer = BruteForceOptimizer(dataset, evaluations, result_writer)
    optimizer.walk()


# stage1_evaluation()


def plot_attr(
    dataset, x_attr, y_attr, x_conv=1.0, y_conv=1.0, x_unit=None, y_unit=None
):
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()
    datas = dataset.find()
    for data in datas:
        legend = dict()
        elements = data["config"]
        for etype, elem in elements.items():
            legend[etype] = elem["name"]
        str(legend).replace("{", "").replace("}", "").replace("'", "")
        x = data[x_attr]["value"] * x_conv
        y = data[y_attr]["value"] * y_conv
        ax.scatter(x, y, label=str(legend))
    ax.legend()
    if x_unit is None:
        x_unit = data[x_attr]["unit"]
    ax.set_xlabel(f"{x_attr} [{x_unit}]")
    if x_unit is None:
        y_unit = data[y_attr]["unit"]
    ax.set_ylabel(f"{y_attr} [{y_unit}]")
    plt.show()


dataset = MongoDataSet(document="results1")
plot_attr(dataset, "energy_density", "stiffness", 1.0, 1e-6, "Wh/kg", "MPa")
