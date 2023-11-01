from typing import cast
from quintus.evals.composites.battery.evaluation import BatteryEvaluation
from quintus.evals.composites.battery.helpers import (
    generate_layup,
    generate_layup_ids,
    get_active_layer,
)
from quintus.structures import get_SI_value, Measurement
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
        eff_capacity = min(anode_capacity, cathode_capacity)

        m_sum = 0
        capacity = 0
        layup = generate_layup(anode, cathode, foil, separator)
        keys = generate_layup_ids()
        usages = list()
        for i in range(len(layup)):
            layer = layup[i]
            layer_properties = cast(Component, layer).properties
            m_sum += get_SI_value(layer_properties.get("thickness")) * get_SI_value(
                layer_properties.get("density")
            )
            usages.append(0)

            index_current = i
            id_current = keys[index_current]

            if id_current not in ["anode", "cathode"]:
                continue
            if (index_other := i - 2) < 0:
                continue
            id_other = keys[index_other]
            if id_other not in ["anode", "cathode"] or id_other == id_current:
                continue

            current = layup[index_current]
            other = layup[index_other]

            active_layer = get_active_layer(current)
            current_active_layers = cast(
                Measurement, active_layer_properties.get("layers")
            ).value
            active_layer = get_active_layer(other)
            other_active_layers = cast(
                Measurement, active_layer_properties.get("layers")
            ).value

            if (
                usages[index_current] < current_active_layers
                and usages[index_other] < other_active_layers
            ):
                capacity = capacity + eff_capacity
                usages[index_current] = usages[index_current] + 1
                usages[index_other] = usages[index_other] + 1

        return capacity * dV / m_sum  #  * anode_layers  # * cathode_layers
