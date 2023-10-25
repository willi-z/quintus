from quintus.evals.composites.battery.evaluation import BatteryEvaluation
from .model import ElectrodeComponent
from ..constants import NUM_ELECTRODE_LAYERS, OUTER_ELECTRODE_LAYER
from quintus.structures import get_SI_value
import numpy as np


class CapacityEvaluation(BatteryEvaluation):
    def __init__(self):
        super().__init__(
            "areal_capacity",
            "C/m^2",
            anode=ElectrodeComponent,
            cathode=ElectrodeComponent,
        )

    def compute_battery(
        self,
        anode: ElectrodeComponent,
        cathode: ElectrodeComponent,
    ) -> float:
        anode_capacity = get_SI_value(anode.areal_capacity)
        cathode_capacity = get_SI_value(cathode.areal_capacity)
        if OUTER_ELECTRODE_LAYER == "anode":
            anode_capacity = anode_capacity * np.ceil(NUM_ELECTRODE_LAYERS / 2)
            cathode_capacity = cathode_capacity * np.floor(NUM_ELECTRODE_LAYERS / 2)
        else:
            anode_capacity = anode_capacity * np.floor(NUM_ELECTRODE_LAYERS / 2)
            cathode_capacity = cathode_capacity * np.ceil(NUM_ELECTRODE_LAYERS / 2)

        # TODO account for two active layer
        return min(anode_capacity, cathode_capacity)
