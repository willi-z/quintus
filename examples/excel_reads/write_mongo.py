from examples.secret_data.my_secret_path import mypath, username, password

from quintus.io.excel import ExcelReader
from quintus.io.mongo import MongoDataWriter


writer = MongoDataWriter(username=username, password=password)

ExcelReader(
    mypath + "quintus_data_v1.0.0.xlsx", mypath + "config_v1.0.0.json", writer
).read_all()
