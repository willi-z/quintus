from quintus.structures import Measurement, Component


class ThicknessComponent(Component):
    properties: dict[str, Measurement] = {
        "thickness": Measurement(),
    }


class ElectrolyteComponent(Component):
    properties: dict[str, Measurement] = {
        "volume_per_capacity": Measurement(),
    }