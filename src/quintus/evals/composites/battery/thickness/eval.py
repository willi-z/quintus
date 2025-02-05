from quintus.evals.composites.battery.battery import Battery
from quintus.evals.composites.battery.evaluation import BatteryEvaluation
from .model import ThicknessComponent, ElectrolyteComponent
from quintus.structures import get_SI_value


class ThicknessEvaluation(BatteryEvaluation):
    def __init__(self):
        super().__init__(
            "thickness",
            "mm",
            anode=ThicknessComponent(),
            cathode=ThicknessComponent(),
            foil=ThicknessComponent(),
            separator=ThicknessComponent(),
            electrolyte=ElectrolyteComponent(),
            required_measurements={"areal_capacity"}
        )

    def compute_battery(
        self,
        battery: Battery
    ) -> float:
        stackup = battery.get_stackup()
        thickness = 0
        for comp_key in stackup:
            comp = battery.composition.components.get(comp_key)
            thickness += get_SI_value(comp.properties.get("thickness"))

        areal_capacity =  get_SI_value(battery.properties.get("areal_capacity"))
        volume_per_capacity = get_SI_value(battery.get_electrolyte().properties.get("volume_per_capacity"))
        thickness += areal_capacity * volume_per_capacity
        return thickness