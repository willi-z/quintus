from pydantic import BaseModel
from quintus.structures import Measurement, Component


class ElectrodeMeasurments(BaseModel):
    # thickness: Measurement
    areal_capacity: Measurement


class ElectrodeComponent(Component):
    properties: ElectrodeMeasurments
