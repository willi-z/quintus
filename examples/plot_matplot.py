from secret_data.my_secret_path import mypath, username, password


from pathlib import Path
import sys
import importlib.util
spec = importlib.util.spec_from_file_location("quintus", str(Path.cwd()/"src/quintus/__init__.py"))
quintus = importlib.util.module_from_spec(spec)
sys.modules["quintus"] = quintus
spec.loader.exec_module(quintus)

from quintus.helpers.parser import parse_unit

from quintus.io.excel import ExcelReader
from quintus.io.mongo import MongoDataWriter, MongoDataSet  # noqa

from quintus.evals.component import ElectrodeCapacityCalc

from quintus.evals.composites.battery import (
    CapacityEvaluation,  # noqa
    StiffnessEvaluation,
    EnergyDensity,
    ArealMass
)
from quintus.structures.component import Component
from quintus.structures.measurement import Measurement

from quintus.walkers import DataFiller
from quintus.walkers.optimization import BruteForceOptimizer

from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.collections import PathCollection
from matplotlib.legend_handler import HandlerPathCollection
from cycler import cycler
import numpy as np

username = None
password = None


light_plots = {
    "lines.color": "black",
    "patch.edgecolor": "black",
    "text.color": "black",
    "axes.prop_cycle": cycler(
       "color", ["#A0B1BA","#9656a2", "#9656a2", "#95cf92", "#f8e16f", "#f4895f", "#de324c"]
    ),
    "axes.linewidth": 1.5,
    "axes.facecolor": "white",
    "axes.edgecolor": "black",
    "axes.labelcolor": "black",
    "xtick.color": "black",
    "ytick.color": "black",
    "figure.facecolor": "white",
    "figure.edgecolor": "white",
    "figure.dpi": 400,
    "axes.labelsize": 20,
    "axes.labelweight": "normal",
    "font.size": 20,
    'font.family' : 'Source Sans 3',
    'lines.markersize':6,
    "legend.handlelength": 1.0,
    "legend.handletextpad": 0.4,
    # grid
    "axes.grid": True,
    "grid.color": "lightgray",
    "grid.linestyle": "dashed",
    # legend
    "legend.fancybox": False,
    "legend.fancybox": False,
    "legend.edgecolor": "black",
    "legend.labelcolor": "black",
    "legend.framealpha": 1.0,
    "savefig.facecolor": "white",
    "savefig.edgecolor": "black",
    # "savefig.transparent": True,
}

colors = ["#6a7893","#640D6B", "#BC5A94", "#369acc", "#7cdd43", "#f8e16f", "#f4895f", "#de324c"]

plot_config = light_plots

plt.rcParams.update(plot_config)

draw_area_of_multifunctionalty = True
el_benchmark = 245 # Wh/kg
mech_benchmark = 30 # GPa
y_max = mech_benchmark +2
x_max = 250

def ray_tracing_method(x,y,poly):

    n = len(poly)
    inside = False

    p1x,p1y = poly[0]
    for i in range(n+1):
        p2x,p2y = poly[i % n]
        if y > min(p1y,p2y):
            if y <= max(p1y,p2y):
                if x <= max(p1x,p2x):
                    if p1y != p2y:
                        xints = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xints:
                        inside = not inside
        p1x,p1y = p2x,p2y

    return inside

def change_marker(handle:PathCollection, original: PathCollection):
    ''' Change the alpha and marker style of the legend handles '''
    handle.update_from(original)
    handle.set_alpha(1)
    handle.set_sizes([130])


def plot_attr(
    dataset,
    x_attr,
    y_attr,
    x_unit=None,
    y_unit=None,
    extra_datas: list[Component] = None,
):
    if dataset is not None:
        datas = dataset.find()
    else:
        datas = dict()
    xs = []
    ys = []
    #legends = []
    for data in datas:
        elements = data["composition"]

        def create_legend() -> str:
            legend = dict()
            for etype, elem in elements.items():
                legend[etype] = elem["name"]
            legend_text = "/".join(legend.values())
            for property in ["areal_mass"]:
                measurment = data["properties"]["areal_mass"]
                val = np.round(measurment["value"], 3)
                unit = measurment["unit"]
                legend_text += "<br>"+f"{property}: {val} {unit}"
            return legend_text

        measurment = data["properties"][x_attr]
        x = measurment["value"] * parse_unit(measurment["unit"]) / parse_unit(x_unit)

        measurment = data["properties"][y_attr]
        y = measurment["value"] * parse_unit(measurment["unit"]) / parse_unit(y_unit)
        xs.append(x)
        ys.append(y)
        
        #legends.append(create_legend())

    fig, ax = plt.subplots(figsize=(5*2,3*2))
    

    if draw_area_of_multifunctionalty:
        polygon_edges = np.array(
            [
                [float(el_benchmark), 0.0], 
                [x_max, 0.0], 
                [x_max, y_max], 
                [0.0, y_max], 
                [0.0, float(mech_benchmark)]
            ],
            dtype=np.float64
        )

        inside_counter = 0
        for i in range(len(xs)):
            if ray_tracing_method(xs[i], ys[i], polygon_edges):
                inside_counter = inside_counter + 1

        print("No. of multifunctional points:", inside_counter)
        polygon = matplotlib.patches.Polygon(polygon_edges, closed=True)
        patch = matplotlib.collections.PatchCollection([polygon], alpha=0.2)
        patch.set_color("#01B04D")
        ax.add_collection(patch)

        # ax.text(x=160, y=30, s="Area of Multi-\nfunctionality", verticalalignment='top', horizontalalignment='right', color='#005500')

    if dataset is not None:
        ax.scatter(xs, ys, label="QUINTUS prediction", color= colors[0], zorder=2.5)

    color_idx = 1
    if extra_datas is None:
        extra_datas = []
    for data in extra_datas:
        measurment = data.properties[x_attr]
        x = measurment.value * parse_unit(measurment.unit) / parse_unit(x_unit)

        measurment = data.properties[y_attr]
        y = measurment.value * parse_unit(measurment.unit) / parse_unit(y_unit)

        ax.scatter([x], [y], label=data.name, color=colors[color_idx], edgecolors='black', zorder=2.5, s=80)
        color_idx = color_idx +1

    if x_unit is None:
        x_unit = data[x_attr]["unit"]
    xlabel = x_attr + " [" + x_unit + "]"
    xlabel = "Energy density" + " [" + x_unit + "]"
    if y_unit is None:
        y_unit = data[y_attr]["unit"]
    ylabel = y_attr + " [" + y_unit + "]"
    ylabel = "Stiffness" + " [" + y_unit + "]"

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_xlim([0, x_max])
    ax.set_ylim([0, y_max])
    fig.tight_layout(pad=0.1)


    if False:
        ax.legend(
            title="Legend",
            loc="upper right",
            handler_map={PathCollection: HandlerPathCollection(update_func=change_marker)}
        )

    if draw_area_of_multifunctionalty:
        outFile = Path().cwd() / ("result_quintus_with_area" + ".png")
    else: 
        outFile = Path().cwd() / ("result_quintus" + ".png")
    plt.savefig(outFile)
    print(f"Saved: {outFile}")


literature_values = [
    Component(
        name="Asp et al.",
        description="Structural Battery from Asp et al.",
        properties={
            "energy_density": Measurement(
                value=24, unit="Wh/kg", source="10.1002/aesr.202000093"
            ),
            "stiffness": Measurement(
                value=25, unit="GPa", source="10.1002/aesr.202000093"
            ),
        },
    ),
    Component(
        name="Saraj et al.",
        description="Structural Battery from Saraj et al.",
        properties={
            "energy_density": Measurement(
                value=41, unit="Wh/kg", source="10.1002/aesr.202300109"
            ),
            "stiffness": Measurement(
                value=26, unit="GPa", source="10.1002/aesr.202300109"
            ),
        },
    ),
    Component(
        name="Meng  et al.",
        description="Structural Battery from Meng et al.",
        properties={
            "energy_density": Measurement(
                value=1.4, unit="Wh/kg", source="10.1021/acs.nanolett.8b03510"
            ),
            "stiffness": Measurement(
                value=7, unit="GPa", source="10.1021/acs.nanolett.8b03510"
            ),
        },
    ),
    Component(
        name="Thakur & Dong",
        description="Structural Battery from Thakur and Dong",
        properties={
            "energy_density": Measurement(
                value=24,
                unit="Wh/kg",
                source="A. Thakur, X. Dong, Manuf. Lett. 2020, 24,1.",
            ),
            "stiffness": Measurement(
                value=0.29,
                unit="GPa",
                source="A. Thakur, X. Dong, Manuf. Lett. 2020, 24,1.",
            ),
        },
    ),
    Component(
        name="Moyler",
        description="Structural Battery from Moyler et al.",
        properties={
            "energy_density": Measurement(
                value=35,
                unit="Wh/kg",
                source="""
K. Moyer, C. Meng, B. Marshall, O. Assal, J. Eaves, D. Perez, R. Karkkainen,
L. Roberson, C. L. Pint, Energy Stor. Mater. 2020, 24,676
""",
            ),
            "stiffness": Measurement(
                value=2,
                unit="GPa",
                source="""
K. Moyer, C. Meng, B. Marshall, O. Assal, J. Eaves, D. Perez, R. Karkkainen,
L. Roberson, C. L. Pint, Energy Stor. Mater. 2020, 24,676
""",
            ),
        },
    ),
    Component(
        name="Liu",
        description="Structural Battery from Liu et al.",
        properties={
            "energy_density": Measurement(
                value=35, unit="Wh/kg", source="10.1016/j.jpowsour.2008.09.082"
            ),
            "stiffness": Measurement(
                value=3, unit="GPa", source="10.1016/j.jpowsour.2008.09.082"
            ),
        },
    ),
    Component(
        name="Comm. Pouchcell",
        description="Common Pouch Bag",
        properties={
            "energy_density": Measurement(
                value=240, unit="Wh/kg", source="10.1002/aesr.202000093"
            ),
            "stiffness": Measurement(
                value=0.7, unit="GPa", source="10.1002/aesr.202000093"
            ),
        },
    ),
]


dataset = MongoDataSet(document="results1", username=username, password=password)
plot_attr(
    dataset,
    "energy_density",
    "stiffness",
    "Wh/kg",
    "GPa",
    extra_datas=literature_values,
)
print("Done")