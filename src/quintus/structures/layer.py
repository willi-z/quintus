from .measurement import Measurement, Measurements
from pydantic import BaseModel, Extra


class Layer(BaseModel, extra=Extra.allow):
    __base__ = Measurements
    material: str
    thickness: Measurement
