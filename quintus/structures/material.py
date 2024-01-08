from .measurement import Measurements
from .layer import Layer
from pydantic import BaseModel, Extra


class Material(BaseModel, extra=Extra.allow):
    __base__: Measurements
    name: str
    description: str = None
    usage: list[str] = None
    layers: list[Layer] = None
