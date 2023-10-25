from pydantic import BaseModel
from quintus.structures import Measurement, Component


class StiffMeasurments(BaseModel):
    thickness: Measurement
    E_t_xx: Measurement
    E_t_yy: Measurement | None
    nu_xy: Measurement
    G_xy: Measurement


class StiffComponent(Component):
    properties: StiffMeasurments
