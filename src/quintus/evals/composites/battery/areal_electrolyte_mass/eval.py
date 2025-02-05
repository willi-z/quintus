from quintus.evals.composites.battery.battery import Battery
from quintus.evals.composites.battery.evaluation import BatteryEvaluation
from quintus.structures import get_SI_value
from .model import ElectrolyteComponent


class ArealElectrolyteMass(BatteryEvaluation):
    def __init__(self):
        super().__init__(
            "areal_electrolyte_mass",
            "kg/m^2",
            electrolyte=ElectrolyteComponent(),
            required_measurements={"areal_capacity"}
        )

    def compute_battery(
        self,
        battery: Battery
    ) -> float:
        electrolyte = battery.get_electrolyte()
        areal_capacity = get_SI_value(battery.properties.get("areal_capacity"))
        electrolyte_mass_per_capacity = get_SI_value(electrolyte.properties.get("electrolyte_mass_per_capacity"))
        result = areal_capacity * electrolyte_mass_per_capacity
        return result 
