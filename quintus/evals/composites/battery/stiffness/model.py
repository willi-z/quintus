from pydantic import BaseModel
from quintus.structures import Measurement, Component


class StiffMeasurments(BaseModel):
    thickness: Measurement = Measurement()
    E_t_xx: Measurement = Measurement()
    E_t_yy: Measurement = None
    nu_xy: Measurement = Measurement()
    G_xy: Measurement = Measurement()


class StiffComponent(Component):
    properties: dict[str, Measurement] = StiffMeasurments()
