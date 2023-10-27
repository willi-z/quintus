from typing import cast
from quintus.evals.composites.battery.evaluation import BatteryEvaluation
from quintus.evals.composites.battery.helpers import get_active_layer
from quintus.structures import get_SI_value
from quintus.structures.component import Component
from .model import WeightComponent, ElectrodeComponent


class EnergyDensity(BatteryEvaluation):
    def __init__(self):
        super().__init__(
            "energy_density",
            "Wh/kg",
            anode=ElectrodeComponent(),
            cathode=ElectrodeComponent(),
            foil=WeightComponent(),
            separator=WeightComponent(),
        )

    def compute_battery(
        self,
        anode: ElectrodeComponent,
        cathode: ElectrodeComponent,
        foil: WeightComponent,
        separator: WeightComponent,
    ) -> float:
        active_layer = get_active_layer(anode)
        active_layer_properties = active_layer.properties
        anode_capacity = get_SI_value(
            active_layer_properties.get("areal_capacity")
        )  # [As/m^2}
        anode_voltage = get_SI_value(anode.properties.get("potential_vs_Li"))  # [V]

        active_layer = get_active_layer(cathode)
        active_layer_properties = active_layer.properties
        cathode_capacity = get_SI_value(
            active_layer_properties.get("areal_capacity")
        )  # [As/m^2}
        cathode_voltage = get_SI_value(cathode.properties.get("potential_vs_Li"))  # [V]
        dV = cathode_voltage - anode_voltage

        m_sum = 0
        layup = [foil, anode, separator, cathode, foil]
        for layer in layup:
            layer_properties = cast(Component, layer).properties
            m_sum += get_SI_value(layer_properties.get("thickness")) * get_SI_value(
                layer_properties.get("density")
            )

        return (
            min(anode_capacity, cathode_capacity)  #  * anode_layers  # * cathode_layers
            * dV
            / m_sum
            / 3600.0
        )
