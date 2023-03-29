from quintus.evals.battery import FastBatterEvaluation
from .model import Electrode


class CapacityEvaluation(FastBatterEvaluation):
    def __init__(self):
        super().__init__(
            "areal_capacity", "C/m^2", {"anode": Electrode, "cathode": Electrode}
        )

    def compute(self, **kwargs) -> float:
        anode = Electrode(kwargs["anode"])
        cathode = Electrode(kwargs["cathode"])
        return min(anode.areal_capacity, cathode.areal_capacity)
