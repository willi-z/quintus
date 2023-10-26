from examples.secret_data.my_secret_path import mypath  # str of directory

from quintus.io.excel import ExcelReader
from quintus.io.sqlite import SqliteDataWriter
from pathlib import Path


writer = SqliteDataWriter(Path().cwd() / "result.sqlite3")

ExcelReader(
    mypath + "quintus_data_v1.0.0.xlsx", mypath + "config_v1.0.0.json", writer
).read_all()
