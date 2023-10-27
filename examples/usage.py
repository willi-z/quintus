from examples.secret_data.my_secret_path import mypath, username, password

from quintus.io.excel import ExcelReader
from quintus.io.mongo import MongoDataWriter, MongoDataSet  # noqa

from quintus.evals.component import ElectrodeCapacityCalc

from quintus.evals.composites.battery import (
    CapacityEvaluation,  # noqa
    StiffnessEvaluation,
    EnergyDensity,
)

from quintus.walkers import DataFiller
from quintus.walkers.optimization import BruteForceOptimizer

writer = MongoDataWriter(username=username, password=password)

ExcelReader(
    mypath + "quintus_data_v1.0.0.xlsx", mypath + "config_v1.0.0.json", writer
).read_all()


save_as_tex = False


def data_extension():
    # Componentwise Dateset-Extension
    evaluations = set()
    evaluations.add(ElectrodeCapacityCalc())
    dataset = MongoDataSet(username=username, password=password)
    result_writer = MongoDataWriter(
        override=False, username=username, password=password
    )  # same set!
    optimizer = DataFiller(dataset, evaluations, result_writer)
    optimizer.walk()


# data_extension()


def stage1_evaluation():
    # first simple evaluation
    evaluations = set()
    # evaluations.add(CapacityEvaluation())
    evaluations.add(StiffnessEvaluation())
    evaluations.add(EnergyDensity())

    dataset = MongoDataSet(username=username, password=password)
    result_writer = MongoDataWriter(
        document="results1", username=username, password=password
    )

    optimizer = BruteForceOptimizer(dataset, evaluations, result_writer)
    optimizer.walk()


stage1_evaluation()


light_plots = {
    "lines.color": "black",
    "patch.edgecolor": "black",
    "text.color": "black",
    # "axes.prop_cycle": cycler(
    #    "color", ["#fcbf49", "#f77f00", "#d62828", "#003049", "#0a9396"]
    # ),
    "axes.linewidth": 1.5,
    "axes.facecolor": "white",
    "axes.edgecolor": "black",
    "axes.labelcolor": "black",
    "xtick.color": "black",
    "ytick.color": "black",
    "figure.facecolor": "white",
    "figure.edgecolor": "white",
    # grid
    "axes.grid": True,
    "grid.color": "lightgray",
    "grid.linestyle": "dashed",
    # legend
    "legend.fancybox": False,
    "legend.edgecolor": "black",
    "legend.labelcolor": "black",
    "legend.framealpha": 1.0,
    "savefig.facecolor": "white",
    "savefig.edgecolor": "black",
    # "savefig.transparent": True,
}


plot_config = light_plots


def plot_attr(
    dataset, x_attr, y_attr, x_conv=1.0, y_conv=1.0, x_unit=None, y_unit=None
):
    import numpy as np
    import matplotlib

    if save_as_tex:
        matplotlib.use("pgf")
        matplotlib.rcParams.update(
            {
                "pgf.texsystem": "pdflatex",
                "text.usetex": True,
                "pgf.rcfonts": False,
            }
        )

    import matplotlib.pyplot as plt

    plt.rcParams.update(plot_config)

    fig, ax = plt.subplots(figsize=(16 * 0.4, 9 * 0.4))
    datas = dataset.find()
    xs = []
    ys = []
    for data in datas:
        elements = data["config"]

        def create_legend() -> str:
            legend = dict()
            for etype, elem in elements.items():
                legend[etype] = elem["name"]
            legend_text = "/".join(legend.values())
            if save_as_tex:
                legend_text = legend_text.replace("_", r"\_")
            return legend_text

        x = data[x_attr]["value"] * x_conv
        y = data[y_attr]["value"] * y_conv
        xs.append(x)
        ys.append(y)
        ax.scatter(x, y, label=create_legend())
    ax.legend()

    if x_unit is None:
        x_unit = data[x_attr]["unit"]
    xlabel = x_attr.replace("_", r"\_")
    ax.set_xlabel(r"$" + xlabel + r"\; \left[" + x_unit + r"\right]$")
    ax.set_xlim(
        np.round(np.floor(np.min(xs) / 20) * 20),
        np.round(np.ceil(np.max(xs) / 20) * 20),
    )

    if y_unit is None:
        y_unit = data[y_attr]["unit"]
    ylabel = y_attr.replace("_", r"\_")
    ax.set_ylabel(r"$" + ylabel + r"\; \left[" + y_unit + r"\right]$")
    ax.set_ylim(np.floor(np.min(ys) / 2) * 2, np.ceil(np.max(ys) / 2) * 2)

    fig.tight_layout(pad=0)
    # plt.show()
    if save_as_tex:
        plt.savefig(mypath + ("quintus" + ".pgf"))
    else:
        plt.savefig(mypath + ("quintus" + ".png"))


dataset = MongoDataSet(document="results1")
plot_attr(dataset, "energy_density", "stiffness", 1.0, 1e-9, "Wh/kg", "GPa")
