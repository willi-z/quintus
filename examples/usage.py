from secrets import mypath  # str of directory

from quintus.io.excel import ExcelReader
from quintus.io.mongo import MongoDataWriter, MongoDataSet  # noqa

from quintus.evals.battery import CapacityEvaluation

from quintus.optimization import Optimizer

writer = MongoDataWriter()

ExcelReader(
    mypath + "quintus_data_v1.0.0.xlsx", mypath + "config_v1.0.0.json", writer
).read_all()


evaluations = []
evaluations.append(CapacityEvaluation())

dataset = MongoDataSet()
result_writer = MongoDataWriter(document="results1")

optimizer = Optimizer(dataset, evaluations, result_writer)
optimizer.search()
