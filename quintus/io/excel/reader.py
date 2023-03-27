from quintus.io import DataWriter
from openpyxl import load_workbook
import json
from pathlib import Path
from quintus.structures import Material, ValidationError
from .configuration import ExcelConfiguration, update_config, ExcelSheet
from quintus.helpers.parser import parse_value
from pprint import pprint


class ExcelReader:
    def __init__(self, filename: str, config_file: str, writer: DataWriter):
        self.wb = load_workbook(filename=filename, data_only=True, read_only=True)

        with Path(config_file).open() as fp:
            config = json.load(fp)

        try:
            self.config = ExcelConfiguration(**config)
        except ValidationError as ex:
            print(ex)

        self.writer = writer

    def read_all(self):
        sheets_names = self.wb.sheetnames
        for sheet_name in sheets_names:
            master_config = self.config.dict()
            master_config.pop("ignore")
            master_config.pop("sheets")
            sheet_config = self.config.sheets.get(sheet_name).dict()
            self.read_sheet(sheet_name, update_config(master_config, sheet_config))

    def read_sheet(self, name: str, config: dict):
        sheet = self.wb[name]
        config = ExcelSheet(**config)
        prefix = []
        names = []
        units = []
        row_number = 0
        for row in sheet.values:
            row_number += 1
            prefix_row = config.pointers.prefix
            if prefix_row is not None:
                if prefix_row == row_number:
                    for value in row:
                        prefix.append(value)

            names_row = config.pointers.names
            if names_row is not None:
                if names_row == row_number:
                    for value in row:
                        names.append(str(value).replace(" ", "_"))

            units_row = config.pointers.units
            if units_row is not None:
                if units_row == row_number:
                    for value in row:
                        units.append(value)

            start_row = config.pointers.start
            if start_row is not None:
                if start_row <= row_number:
                    material_data = dict()
                    layer_ids = list()

                    if config.flag is not None:
                        flag_field = config.flag.field
                    if material_data.get(flag_field) is None:
                        material_data[flag_field] = []
                    material_data[flag_field].append(config.flag.flag_as)

                    for i in range(len(row)):
                        cell_val = row[i]
                        if cell_val is None:
                            continue

                        cell_name = names[i]
                        cell_unit = units[i]
                        cell_prefix = prefix[i]

                        value = {"value": cell_val}
                        if isinstance(cell_val, str):
                            if "+/-" in cell_val:
                                cell_val, tol = parse_value(cell_val)
                                value = {"value": cell_val, "tol": tol}
                        if cell_unit is not None:
                            value.update({"unit": cell_unit})

                        if cell_name in {"name", "description", "material"}:
                            value = cell_val

                        if cell_prefix is not None:
                            if "layer" in cell_prefix:
                                if material_data.get("layers") is None:
                                    material_data["layers"] = list()

                                if cell_prefix not in layer_ids:
                                    layer_ids.append(cell_prefix)
                                    material_data["layers"].append(
                                        {"description": cell_prefix}
                                    )
                                layer_id = layer_ids.index(cell_prefix)

                                layer = material_data["layers"][layer_id]
                                layer.update({cell_name: value})
                                continue
                            else:
                                measured_at = json.loads(cell_prefix)
                                value.update({"at": measured_at})

                        material_data.update({cell_name: value})

                    try:
                        material = Material(**material_data)
                        self.writer.write_entry(material.dict())
                        # pprint(material.dict())
                    except ValidationError as err:
                        print(f"Error: {material_data['name']}")
                        print(err)
                        print("# Got:")
                        pprint(material_data)
                        print("####################")
