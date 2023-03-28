import pytest
from quintus.helpers.parser import parse_unit, parse_value
import numpy as np


@pytest.mark.parametrize(
    "unit, value", [("cm^2", 1e-4), ("mg/cm^2", 1e-2), ("mAh/g", 3600)]
)
def test_units(unit: str, value):
    assert np.isclose(parse_unit(unit), value)


@pytest.mark.parametrize(
    "value_str, norm, minimum, maximum",
    [
        ("1.3", 1.3, 0.0, 0.0),
        ("3.563(+/-0.18)", 3.563, -0.18, +0.18),
        ("3.563  (+/- 0.18)", 3.563, -0.18, +0.18),
    ],
)
def test_values(value_str: str, norm: float, minimum: float, maximum: float):
    value, tol = parse_value(value_str)
    assert np.isclose(value, norm)

    assert np.isclose(tol[0], minimum)
    assert np.isclose(tol[1], maximum)
