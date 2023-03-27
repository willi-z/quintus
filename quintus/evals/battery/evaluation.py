from quintus.evals import Evaluation
from typing import Type
from abc import abstractmethod
from quintus.structures import Measurements


class BatteryEvaluation(Evaluation):
    def __init__(
        self,
        anode_cls: Type[Measurements],
        cathode_cls: Type[Measurements],
        foil_cls: Type[Measurements],
        separator_cls: Type[Measurements],
    ):
        self.anode_cls = anode_cls
        self.cathode_cls = cathode_cls
        self.foil_cls = foil_cls
        self.separator_cls = separator_cls

    def get_args_form(self) -> dict[str, Type[Measurements]]:
        return {
            "anode": self.anode_cls,
            "cathode": self.cathode_cls,
            "foil": self.foil_cls,
            "separator": self.separator_cls,
        }

    def evaluate(self, **kwargs) -> float:
        return self.evaluate_stack(**kwargs)

    @abstractmethod
    def evaluate_stack(
        self,
        anode: Measurements,
        cathode: Measurements,
        foil: Measurements,
        separator: Measurements,
    ) -> float:
        pass
