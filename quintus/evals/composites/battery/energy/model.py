from quintus.structures import Measurement, Component


class ElectrodeComponent(Component):
    properties: dict[str, Measurement] = {
        "potential_vs_Li": Measurement(),
        "areal_mass": Measurement(),
    }
    composition: dict[str, Component] = {
        "active layer": Component(
            properties={"areal_capacity": Measurement(), "layers": Measurement()}
        )
    }


class WeightComponent(Component):
    properties: dict[str, Measurement] = {
        "areal_mass": Measurement(),
    }
