from openpyxl.cell import Cell
from openpyxl.worksheet.worksheet import Worksheet


class ExcelValueLegend:
    def __init__(self, sheet: Worksheet) -> None:
        self.color_coding = dict()
        self.read_legend(sheet)

    def get_cell_color(self, cell: Cell) -> str | None:
        if cell.fill is None:
            return None
        color = cell.fill.bgColor
        if color is None:
            return None
        return color.rgb

    def get_value_type(self, cell: Cell) -> str | None:
        color = self.get_cell_color(cell)
        return self.color_coding.get(color)

    def read_legend(self, sheet: Worksheet):
        index = 1
        while True:
            cell = sheet.cell(row=index, column=1)
            value = cell.value
            color = self.get_cell_color(cell)
            if value is None or str(value) == "" or color == "FFFFFF":
                break
            if "Imaginärer Wert" in value:
                value = "approximation"
            elif "Literatur" in value:
                value = "literature"
            elif "Experimentell" in value:
                value = "experiment"
            elif "rechnet" in value:
                value = "computation"
            self.color_coding[color] = value
            index = index + 1
