from quintus.io.datawriter import DataWriter
from quintus.io.excel.reader import ExcelReader
from quintus.structures import Component


def test_reader():
    class TestWriter(DataWriter):
        def __init__(self):
            self.data = dict()

        def write_entry(self, entry: Component) -> None:
            key = entry.name
            self.data[key] = entry.dict()

    writer = TestWriter()
    reader = ExcelReader(
        "tests/resources/test_set1.xlsx", "tests/resources/test_set1.json", writer
    )
    reader.read_all()

    findings = list(writer.data.keys())
    results = [
        "ElViS_p_1",
        "ElViS_p_2",
        "ElViS_s_1",
        "ElViS_s_2",
        "ELVIS_a_1",
        "ELVIS_a_2",
        "ELVIS_a_3",
        "ELVIS_a_4",
        "ElVis_c_1",
        "ElVis_c_2",
        "ElVis_c_3",
    ]
    assert len(findings) == len(results)
    for i in range(len(results)):
        assert findings == results
