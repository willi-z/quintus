from quintus.structures import Component, Measurement


class ElectrodeComponent(Component):
    composition: dict[str, Component] = {
        "active layer": Component(
            properties={"areal_capacity": Measurement(), "layers": Measurement()}
        )
    }
