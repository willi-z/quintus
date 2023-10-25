from pydantic import BaseModel
from quintus.structures import Measurement, Component


class ElectrodeMeasurments(BaseModel):
    potential_vs_Li: Measurement
    thickness: Measurement
    density: Measurement


class ElectrodeComponent(Component):
    properties: ElectrodeMeasurments


class WeightMeasurments(BaseModel):
    thickness: Measurement
    density: Measurement


class WeightComponent(Component):
    properties: WeightMeasurments
