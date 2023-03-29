from quintus.evals.battery import FastBatterEvaluation
from .model import StiffMaterial


class StiffnessEvaluation(FastBatterEvaluation):
    def __init__(self):
        super().__init__(
            "areal_capacity",
            "C/m^2",
            {
                "anode": StiffMaterial,
                "cathode": StiffMaterial,
                "foil": StiffMaterial,
                "separator": StiffMaterial,
            },
            {
                "anode": "anode",
                "cathode": "cathode",
                "foil": "foil",
                "separator": "separator",
            },
        )

    def compute(self, **kwargs) -> float:
        anode = StiffMaterial(kwargs["anode"])
        cathode = StiffMaterial(kwargs["cathode"])
        return min(anode.areal_capacity, cathode.areal_capacity)
