from typing import cast
from quintus.evals.composites.battery.battery import Battery
from quintus.evals.composites.battery.evaluation import BatteryEvaluation
from quintus.evals.composites.battery.helpers import (
    get_active_layer,
)
from quintus.structures.measurement import Measurement
from .model import ElectrodeComponent
from quintus.structures import get_SI_value


class CapacityEvaluation(BatteryEvaluation):
    def __init__(self):
        super().__init__(
            "areal_capacity",
            "mAh/m^2",
            anode=ElectrodeComponent(),
            cathode=ElectrodeComponent(),
        )

    def compute_battery(
        self,
        battery: Battery
    ) -> float:
        active_layer = get_active_layer(battery.get_anode())
        active_layer_properties = active_layer.properties
        anode_capacity = get_SI_value(active_layer_properties.get("areal_capacity"))
        active_layer = get_active_layer(battery.get_anode())
        active_layer_properties = active_layer.properties
        cathode_capacity = get_SI_value(
            active_layer_properties.get("areal_capacity")
        )  # [As/m^2}
        eff_capacity = min(anode_capacity, cathode_capacity)
        capacity = 0

        stackup = battery.get_stackup()
        usages = list()
        for i in range(len(stackup)):
            usages.append(0)

            index_current = i
            current_component_key = stackup[index_current]

            if current_component_key not in ["anode", "cathode"]:
                continue
            if (index_last_electrode := index_current - 2) < 0:
                continue
            previous_electrode_key = stackup[index_last_electrode]
            if previous_electrode_key not in ["anode", "cathode"] or current_component_key == previous_electrode_key:
                continue

            electrode_current = battery.composition.components[current_component_key]
            electrode_previous = battery.composition.components[previous_electrode_key]

            active_layer = get_active_layer(electrode_current)
            current_active_layers = cast(
                Measurement, active_layer_properties.get("layers")
            ).value
            active_layer = get_active_layer(electrode_previous)
            previous_active_layers = cast(
                Measurement, active_layer_properties.get("layers")
            ).value

            if (
                usages[index_current] < current_active_layers
                and usages[index_last_electrode] < previous_active_layers
            ):
                capacity = capacity + eff_capacity
                usages[index_current] = usages[index_current] + 1
                usages[index_last_electrode] = usages[index_last_electrode] + 1
        return capacity
