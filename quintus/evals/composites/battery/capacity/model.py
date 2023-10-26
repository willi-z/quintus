from quintus.structures import Component, Measurement


class ElectrodeComponent(Component):
    properties: dict[str, Measurement] = {"areal_capacity": Measurement()}
