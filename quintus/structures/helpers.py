from typing import Type
from pydantic import BaseModel
from .measurement import Measurement
from quintus.helpers import parse_unit


def generate_attr_filter(model: Type[BaseModel], usage: str | None = None) -> dict:
    fields = model.__fields__
    attr_filter = []
    if usage is not None:
        attr_filter.append({"usage": {"$in": [usage]}})
    for attr, field in fields.items():
        if not field.required:
            continue
        attr_filter.append({attr: {"$exists": True}})

    return {"$and": attr_filter}


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
