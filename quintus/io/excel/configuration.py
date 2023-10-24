from pydantic import BaseModel
from .pointers import Pointers
from .flag import Flag


class ExcelSheetConfiguration(BaseModel):
    flag: Flag
    pointers: Pointers = None
    transforms: dict[str, str] = None


class ExcelConfiguration(BaseModel):
    ignore: list[str] = None
    sheets: dict[str, ExcelSheetConfiguration] = None
    pointers: Pointers = None
    transforms: dict[str, str] = None

    # def __init__(self, **data):
    #     super().__init__(**data)
    #     for _, sheet in self.sheets.items():
    #         print(sheet)
    #         if sheet.pointers is None:
    #             sheet.pointers = Pointers()
    #         sheet.pointers.update(**self.pointers.dict())
    #         print(sheet)


def update_config(master, slave):
    if master is None:
        return slave
    if isinstance(slave, dict):
        for key, value in slave.items():
            new_config = update_config(dict(master).get(key), value)
            master[key] = new_config
        return master
    else:
        if slave is None:
            return master
        else:
            return slave
