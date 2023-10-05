from quintus.evals.battery import FastBatterEvaluation
from .model import Electrode
from ..constants import NUM_ELECTRODE_LAYERS, OUTER_ELECTRODE_LAYER
from quintus.structures import get_SI_value
import numpy as np


class CapacityEvaluation(FastBatterEvaluation):
    def __init__(self):
        super().__init__(
            "areal_capacity", "C/m^2", {"anode": Electrode, "cathode": Electrode}
        )

    def compute(self, **kwargs) -> float:
        anode = Electrode(**kwargs["anode"])
        cathode = Electrode(**kwargs["cathode"])
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
