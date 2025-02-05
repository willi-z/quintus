import pytest
import numpy as np
from src.quintus.helpers.parser import parse_unit


@pytest.mark.parametrize(
    "non_si_unit,conversion_factor",
    [
        ("mA/m^2", 1e-3),("Ah", 60*60), ("mAh/m^2", 1e-3*60*60), ("g/mAh", 1.0/(60*60)),
        ("Wh/kg", 60*60),
        ("GPa", 1e9),
        ("µm", 1e-6),
        ("µL", 1e-9)
    ],
)
def test_unit_conversions(non_si_unit, conversion_factor):
    assert np.isclose(parse_unit(non_si_unit),conversion_factor)