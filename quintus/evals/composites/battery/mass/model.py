from quintus.structures import Measurement, Component


class WeightComponent(Component):
    properties: dict[str, Measurement] = {
        "areal_mass": Measurement(),
    }