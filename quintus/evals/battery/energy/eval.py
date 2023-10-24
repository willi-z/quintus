from quintus.evals.battery import BatteryEvaluation
from quintus.structures import get_SI_value, Measurement
from quintus.evals.battery.helpers import get_active_layer
from .model import WeightMaterial, ElectrodeMaterial


class EnergyDensity(BatteryEvaluation):
    def __init__(self):
        super().__init__(
            "energy_density",
            "Wh/kg",
            anode=ElectrodeMaterial,
            cathode=ElectrodeMaterial,
            foil=WeightMaterial,
            separator=WeightMaterial,
        )

    def compute_battery(
        self,
        anode: ElectrodeMaterial,
        cathode: ElectrodeMaterial,
        foil: WeightMaterial,
        separator: WeightMaterial,
    ) -> float:
        active_layer = get_active_layer(anode)
        areal_capacity = Measurement(**active_layer.__dict__.get("areal_capacity"))
        # layers = Measurement(**active_layer.__dict__.get("layers"))
        anode_capacity = get_SI_value(areal_capacity)  # [As/m^2}
        # anode_layers = get_SI_value(layers)  # []
        anode_voltage = get_SI_value(anode.potential_vs_Li)  # [V]

        active_layer = get_active_layer(cathode)
        areal_capacity = Measurement(**active_layer.__dict__.get("areal_capacity"))
        # layers = Measurement(**active_layer.__dict__.get("layers"))
        cathode_capacity = get_SI_value(areal_capacity)  # [As/m^2}
        # cathode_layers = get_SI_value(layers)  # []
        cathode_voltage = get_SI_value(cathode.potential_vs_Li)  # [V]

        dV = cathode_voltage - anode_voltage

        m_sum = 0
        layup = [foil, anode, separator, cathode, foil]
        for layer in layup:
            m_sum += get_SI_value(layer.thickness) * get_SI_value(layer.density)

        return (
            min(anode_capacity, cathode_capacity)  #  * anode_layers  # * cathode_layers
            * dV
            / m_sum
            / 3600.0
        )
