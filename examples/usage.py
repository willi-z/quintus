from secrets import mypath  # str of directory

from quintus.io.excel import ExcelReader
from quintus.io.mongo import MongoDataWriter, MongoDataSet  # noqa

from quintus.evals import collect_required_attr, generate_filters
from quintus.evals.battery import CapacityEvaluation


writer = MongoDataWriter()

ExcelReader(
    mypath + "quintus_data_v1.0.0.xlsx", mypath + "config_v1.0.0.json", writer
).read_all()


evaluations = []
evaluations.append(CapacityEvaluation())

requirements = collect_required_attr(evaluations)
filters = generate_filters(requirements)

dataset = MongoDataSet()
for key, filter in filters.items():
    print(filter)
    print(f"for {key} found:")
    results = dataset.find(filter)
    for res in results:
        print(res["name"])
    print("##################")
