from quintus.structures import Component, Composition, Measurement


class ElectrodeComponent(Component):
    composition: Composition = Composition(
        component = {
            "active layer": Component(
                properties={"layers": Measurement()}
            )
        }
    )