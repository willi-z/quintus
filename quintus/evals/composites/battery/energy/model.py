from quintus.structures import Measurement, Component


class ElectrodeComponent(Component):
    properties: dict[str, Measurement] = {
        "potential_vs_Li": Measurement(),
    }
