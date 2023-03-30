from quintus.evals.battery import FastBatterEvaluation
from .model import Electrode
from quintus.structures import get_SI_value


class CapacityEvaluation(FastBatterEvaluation):
    def __init__(self):
        super().__init__(
            "areal_capacity", "C/m^2", {"anode": Electrode, "cathode": Electrode}
        )

    def compute(self, **kwargs) -> float:
        anode = Electrode(**kwargs["anode"])
        cathode = Electrode(**kwargs["cathode"])
        return min(
            get_SI_value(anode.areal_capacity), get_SI_value(cathode.areal_capacity)
        )
