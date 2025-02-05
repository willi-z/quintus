from quintus.evals.composites.battery.battery import Battery
from quintus.evals.composites.battery.evaluation import BatteryEvaluation
from quintus.structures import get_SI_value
from .model import WeightComponent


class ArealMass(BatteryEvaluation):
    def __init__(self):
        super().__init__(
            "areal_mass",
            "kg/m^2",
            anode=WeightComponent(),
            cathode=WeightComponent(),
            foil=WeightComponent(),
            separator=WeightComponent(),
            required_measurements={"areal_electrolyte_mass"}
        )

    def compute_battery(
        self,
        battery: Battery
    ) -> float:
        m_sum = 0
        stackup = battery.get_stackup()
        for key in stackup:
            layer = battery.composition.components[key]
            layer_properties = layer.properties
            m_sum += get_SI_value(layer_properties.get("areal_mass"))
        m_sum += get_SI_value(battery.properties.get("areal_electrolyte_mass"))
        return m_sum 
