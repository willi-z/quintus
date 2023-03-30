from secrets import mypath  # str of directory

from quintus.io.excel import ExcelReader
from quintus.io.mongo import MongoDataWriter, MongoDataSet  # noqa

from quintus.evals.battery.component import ElectrodeCapacityCalc

from quintus.evals.battery import CapacityEvaluation, StiffnessEvaluation

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


data_extension()


def stage1_evaluation():
    # first simple evaluation
    evaluations = set()
    evaluations.add(CapacityEvaluation())
    evaluations.add(StiffnessEvaluation())

    dataset = MongoDataSet()
    result_writer = MongoDataWriter(document="results1")

    optimizer = BruteForceOptimizer(dataset, evaluations, result_writer)
    optimizer.walk()


stage1_evaluation()
