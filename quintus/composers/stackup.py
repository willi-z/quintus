from .composer import Composer
from quintus.structures import Component, Composition
from typing import Callable

class StackupComposer(Composer):
    def __init__(self, num_layer: int, layer_generator: Callable[[int], list[str]]):
        stackup = layer_generator(num_layer)
        for key in stackup:
            if not self.is_compatible_with(key):
                raise RuntimeError(f"Composer {self.__class__} does not know what to do with '{key}'! Therefore {layer_generator} is incompatible!")
        self.stackup = stackup
        
    def generate(self, components: dict[str, Component]) -> Composition:
        return Composition(
            type="stackup", 
            components=components,
            options= {
                "stackup": self.stackup
            }
        )