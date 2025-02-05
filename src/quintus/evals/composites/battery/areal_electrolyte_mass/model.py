from quintus.structures import Measurement, Component


class ElectrolyteComponent(Component):
    properties: dict[str, Measurement] = {
        "electrolyte_mass_per_capacity": Measurement(),
    }