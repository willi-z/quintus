from quintus.evals.battery import BatteryEvaluation
from quintus.structures import Measurements
from .model import Electrode


class CapacityEvaluation(BatteryEvaluation):
    def __init__(self):
        super().__init__(Electrode, Electrode, Measurements, Measurements)

    def evaluate_stack(
        self,
        anode: Electrode,
        cathode: Electrode,
        foil: Measurements,
        separator: Measurements,
    ) -> float:
        return anode.thickness + cathode.thickness
