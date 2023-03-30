from quintus.evals.battery import FastBatterEvaluation
from .model import StiffMaterial
from quintus.structures import get_SI_value


class StiffnessEvaluation(FastBatterEvaluation):
    def __init__(self):
        super().__init__(
            "stiffness",
            "N/m^2",
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
        anode = StiffMaterial(**kwargs["anode"])
        cathode = StiffMaterial(**kwargs["cathode"])
        return (get_SI_value(anode.E_t_xx) + get_SI_value(cathode.E_t_xx)) / 2
