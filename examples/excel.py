from my_secret_path import mypath  # str of directory

from quintus.io.excel import ExcelReader
from quintus.io.json import JSONDataWriter
from pathlib import Path


writer = JSONDataWriter(Path().cwd() / "result.json")

ExcelReader(
    mypath + "quintus_data_v1.0.0.xlsx", mypath + "config_v1.0.0.json", writer
).read_all()
