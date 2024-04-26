from ..composer import Composer
from quintus.structures import Component, Composition

class ElectrodeComposer(Composer):
    def generate(self, components: dict[str, Component]) -> Composition:
        return Composition(type="electrode",
                components=components,
                options = dict()
            )

    def is_compatible_with(self, component_key: str) -> bool:
        return component_key in {"active layer", "substrate layer"}