import pytest
from src.quintus.structures.helpers import get_SI_value
from src.quintus.structures.measurement import Measurement
import numpy as np

@pytest.mark.parametrize(
    "non_si_unit,conversion_factor",
    [("mA/m^2", 1e-3),("Ah", 60*60), ("mAh/m^2", 1e-3*60*60), ("g/mAh", 1.0/(60*60))],
)
def test_unit_conversions(non_si_unit, conversion_factor):
    assert np.isclose(get_SI_value(Measurement(value=1.0, unit=non_si_unit)),conversion_factor)