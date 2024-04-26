from quintus.evals.composites.battery.battery import Battery
from quintus.evals.composites.battery.evaluation import BatteryEvaluation
from quintus.evals.composites.battery.helpers import (
    get_active_layer,
)
from quintus.structures import get_SI_value
from .model import  ElectrodeComponent


class EnergyDensity(BatteryEvaluation):
    def __init__(self):
        super().__init__(
            "energy_density",
            "Wh/kg",
            required_measurements={"areal_mass", "areal_capacity"},
            anode=ElectrodeComponent(),
            cathode=ElectrodeComponent()
        )

    def compute_battery(
        self,
        battery: Battery
    ) -> float:
        anode = battery.get_anode()
        anode_voltage = get_SI_value(anode.properties.get("potential_vs_Li"))  # [V]

        cathode = battery.get_cathode()
        cathode_voltage = get_SI_value(cathode.properties.get("potential_vs_Li"))  # [V]
        dV = cathode_voltage - anode_voltage
        capacity = get_SI_value(battery.properties.get("areal_capacity"))
        m_sum = get_SI_value(battery.properties.get("areal_mass"))

        return capacity * dV / m_sum  #  * anode_layers  # * cathode_layers
