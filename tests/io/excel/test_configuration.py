from pathlib import Path
import json
import pytest
from quintus.io.excel.configuration import ExcelConfiguration, update_config
from pydantic import ValidationError


def test_valid_config():
    success = True
    with Path("tests/resources/test_set1.json").open() as fp:
        config = json.load(fp)

    try:
        config = ExcelConfiguration(**config)
    except ValidationError as ex:
        print(ex)
        success = False

    print(config)
    assert success


@pytest.mark.parametrize(
    "master, slave, exp_result",
    [
        ({"a": 1}, {"a": 2}, {"a": 2}),
        ({"ma": {"a": 1, "b": 0}}, {"ma": {"b": 2}}, {"ma": {"a": 1, "b": 2}}),
        ({"ma": {"a": 1}}, {"ma": {"b": 2}}, {"ma": {"a": 1, "b": 2}}),
    ],
)
def test_update_config(master, slave, exp_result):
    result = update_config(master, slave)
    assert result == exp_result


if __name__ == "__main__":
    # test_valid_config()
    test_update_config({"a": 1}, {"a": 2}, {"a": 2})
