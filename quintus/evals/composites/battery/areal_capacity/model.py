from quintus.structures import Component, Composition, Measurement


class ElectrodeComponent(Component):
    composition: Composition = Composition(
        component = {
        "active layer": Component(
            properties={"areal_capacity": Measurement(), "layers": Measurement()}
        )
        }
    )
 # type: ignore