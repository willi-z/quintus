from secret_data.my_secret_path import mypath, username, password


from pathlib import Path
import sys
import importlib.util
spec = importlib.util.spec_from_file_location("quintus", str(Path.cwd()/"quintus/__init__.py"))
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

import plotly.graph_objects as go
import numpy as np

username = None
password = None

def is_special(data: dict) -> bool:
    elements = data["composition"]
    if "ElViS_p_6" in [element["name"] for element in elements.values()]:
        return True
    return False


def plot_attr(
    dataset,
    x_attr,
    y_attr,
    x_unit=None,
    y_unit=None,
    extra_datas: list[Component] = None,
):
    datas = dataset.find()
    results = {
        'x' : [],
        'y' : [],
        'text' : []
    }
    specials = {
        'x' : [],
        'y' : [],
        'text' : []
    }
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
        if is_special(data):
            specials["x"].append(x/2)
            specials["y"].append(y/8)
            specials["text"].append(create_legend())
        else:
            results["x"].append(x/2)
            results["y"].append(y/8)
            results["text"].append(create_legend())

    fig = go.Figure()
    fig.add_trace(go.Scatter( name="Quintus", marker_size=10, **results))
    fig.add_trace(go.Scatter( name="Quintus specials", marker_size=10, **specials))

    if extra_datas is None:
        extra_datas = []
    for data in extra_datas:
        measurment = data.properties[x_attr]
        x = measurment.value * parse_unit(measurment.unit) / parse_unit(x_unit)

        measurment = data.properties[y_attr]
        y = measurment.value * parse_unit(measurment.unit) / parse_unit(y_unit)
        fig.add_trace(
            go.Scatter(x=[x], y=[y], text=data.name, marker_size=10, name=data.name)
        )

    fig.update_traces(mode="markers", marker={"sizemode": "area", "sizeref": 10})

    if x_unit is None:
        x_unit = data[x_attr]["unit"]
    xlabel = x_attr + " [" + x_unit + "]"
    if y_unit is None:
        y_unit = data[y_attr]["unit"]
    ylabel = y_attr + " [" + y_unit + "]"

    fig.update_layout(
        title="Quintus Results",
        xaxis_title=xlabel,
        yaxis_title=ylabel,
        legend_title="Legend Title",
    )
    outFile = Path().cwd() / ("result_quintus" + ".html")
    fig.write_html(outFile)
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