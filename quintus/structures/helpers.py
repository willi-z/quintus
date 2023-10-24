from .measurement import Measurement
from quintus.helpers import parse_unit


def get_SI_value(measurement: Measurement) -> float:
    return measurement.value * parse_unit(measurement.unit)


def get_SI_tol(measurement: Measurement) -> tuple[float, float]:
    if measurement.tol is not None:
        tols = measurement.tol
        unit_convertion = parse_unit(measurement.unit)
        return (
            tols[0] * unit_convertion,
            tols[1] * unit_convertion,
        )
    else:
        return (0.0, 0.0)
