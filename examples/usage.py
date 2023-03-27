from quintus.evals.battery import CapacityEvaluation
from quintus.io.excel import ExcelReader
from quintus.io.mongo import MongoDataWriter, MongoDataSet  # noqa
from secrets import mypath  # str of directory


writer = MongoDataWriter()

ExcelReader(
    mypath + "quintus_data_v1.0.0.xlsx", mypath + "config_v1.0.0.json", writer
).read_all()


evaluation = CapacityEvaluation()
form = evaluation.get_args_form()
# print(form)

usages = dict()

for key, attr in form.items():
    if usages.get(key) is None:
        usages[key] = list()

    usages[key].append(attr)

# print(usages)

dataset = MongoDataSet()
dataset.reduce_set(usages)
