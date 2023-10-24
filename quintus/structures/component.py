from .measurement import Measurement
from pydantic import BaseModel, Extra


class Component(BaseModel, extra=Extra.allow):
    _id: str
    name: str = None
    description: str = None
    tags: set[str] = None
    properties: dict[str, Measurement] = None
    compostion: dict[str, "Component"] = None

    def is_valid(self) -> bool:
        if self.name is None:
            return False
        if self.compostion is not None:
            for component in self.compostion.values():
                if not component.is_valid():
                    return False
        return True
