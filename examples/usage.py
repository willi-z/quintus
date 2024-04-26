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

from quintus.composers.battery import ElectrodeComposer, LayerComposer, PhaseComposer

from quintus.evals.component import ElectrodeCapacityCalc

from quintus.evals.composites.battery import (
    BatteryStackupComposer,
    CapacityEvaluation,  # noqa
    ArealElectrolyteMass,
    StiffnessEvaluation,
    EnergyDensity,
    ArealMass
)
from quintus.structures.component import Component
from quintus.structures.measurement import Measurement

from quintus.walkers import DataFiller
from quintus.walkers.optimization import BruteForceOptimizer
import numpy as np
import logging

logging.basicConfig(filename='quintus.log', level=logging.INFO)

from pathlib import Path

username = None
password = None

def read_from_excel():
    writer = MongoDataWriter(
        username=username, password=password
    )

    ExcelReader(
        mypath + "quintus_data_v1.0.0.xlsx", mypath + "config_v1.0.0.json", writer,
        composers={ElectrodeComposer(), LayerComposer(), PhaseComposer()}
    ).read_all()

# read_from_excel()


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

#exit()


def stage1_evaluation():
    NUM_ELECTRODE_LAYERS = 19  # number of battery layers
    OUTER_ELECTRODE_LAYER = "anode"  # can either be "cathode" or "anode"
    # first simple evaluation
    composer = BatteryStackupComposer(NUM_ELECTRODE_LAYERS, OUTER_ELECTRODE_LAYER)
    evaluations = set()
    evaluations.add(CapacityEvaluation())
    evaluations.add(ArealElectrolyteMass())
    evaluations.add(StiffnessEvaluation())
    evaluations.add(EnergyDensity())
    evaluations.add(ArealMass())

    dataset = MongoDataSet(username=username, password=password)
    result_writer = MongoDataWriter(
        document="results1", username=username, password=password
    )

    optimizer = BruteForceOptimizer(dataset, composer, evaluations, result_writer)
    optimizer.walk()


stage1_evaluation()

print("Done")