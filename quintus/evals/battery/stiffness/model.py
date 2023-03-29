from pydantic import BaseModel
from quintus.structures import Measurement


class StiffMaterial(BaseModel):
    thickness: Measurement
    E_t_xx: Measurement
    E_t_yy: Measurement | None
