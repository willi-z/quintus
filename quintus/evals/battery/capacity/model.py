from pydantic import BaseModel
from quintus.structures import Measurement


class Electrode(BaseModel):
    thickness: Measurement
    area_mass: Measurement
