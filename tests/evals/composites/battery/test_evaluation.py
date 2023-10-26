import pytest
from typing import Type
from pydantic import BaseModel
from quintus.structures import Component, Measurement
from quintus.evals.composites.battery.evaluation import generate_attribute_filter


class ElectrodeMeasurments(BaseModel):
    potential_vs_Li: Measurement
    thickness: Measurement
    density: Measurement


class ElectrodeComponent(Component):
    properties: ElectrodeMeasurments


@pytest.mark.parametrize(
    "cls, result",
    [
        (
            ElectrodeComponent,
            {
                "properties": {
                    "potential_vs_Li": {"$exists": True},
                    "thickness": {"$exists": True},
                    "density": {"$exists": True},
                }
            },
        )
    ],
)
def test_generate_attribute_filter(cls: Type[Component], result):
    assert generate_attribute_filter(cls) == result
