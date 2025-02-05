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
            "Ah/m^2",
            anode=ElectrodeComponent(),
            cathode=ElectrodeComponent(),
            required_measurements={"cells"}
        )

    def compute_battery(
        self,
        battery: Battery
    ) -> float:
        active_layer = get_active_layer(battery.get_anode())
        active_layer_properties = active_layer.properties
        anode_capacity = get_SI_value(active_layer_properties.get("areal_capacity"))
        active_layer = get_active_layer(battery.get_cathode())
        active_layer_properties = active_layer.properties
        cathode_capacity = get_SI_value(
            active_layer_properties.get("areal_capacity")
        )  # [As/m^2}
        eff_capacity = min(anode_capacity, cathode_capacity)
        capacity = get_SI_value(battery.properties.get("cells")) * eff_capacity
        return capacity
