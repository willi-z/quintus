from quintus.io.reader import read_excel


def test_reader():
    read_excel("tests/io/test_set1.xlsx", "tests/io/config.json")
    assert True
