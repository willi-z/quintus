from typing import cast
from quintus.evals.composites.battery.evaluation import BatteryEvaluation
from quintus.evals.composites.battery.helpers import (
    generate_layup,
)
from quintus.structures import get_SI_value
from quintus.structures.component import Component
from .model import WeightComponent


class ArealMass(BatteryEvaluation):
    def __init__(self):
        super().__init__(
            "areal_mass",
            "kg/m**2",
            anode=WeightComponent(),
            cathode=WeightComponent(),
            foil=WeightComponent(),
            separator=WeightComponent(),
        )

    def compute_battery(
        self,
        anode: WeightComponent,
        cathode: WeightComponent,
        foil: WeightComponent,
        separator: WeightComponent,
    ) -> float:
        m_sum = 0
        layup = generate_layup(anode, cathode, foil, separator)
        for i in range(len(layup)):
            layer = layup[i]
            layer_properties = cast(Component, layer).properties
            m_sum += get_SI_value(layer_properties.get("areal_mass"))

        return m_sum 
