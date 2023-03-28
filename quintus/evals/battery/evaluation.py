from quintus.evals import Evaluation
from typing import Type
from abc import abstractmethod
from quintus.structures import Measurements, collect_model_attr


class BatteryEvaluation(Evaluation):
    def __init__(
        self,
        anode_cls: Type[Measurements] | None,
        cathode_cls: Type[Measurements] | None,
        foil_cls: Type[Measurements] | None,
        separator_cls: Type[Measurements] | None,
    ):
        self.anode_cls = anode_cls
        self.cathode_cls = cathode_cls
        self.foil_cls = foil_cls
        self.separator_cls = separator_cls

    def get_required_attrs(self) -> dict[set[str]]:
        return {
            "anode": collect_model_attr(self.anode_cls),
            "cathode": collect_model_attr(self.cathode_cls),
            "foil": collect_model_attr(self.foil_cls),
            "separator": collect_model_attr(self.separator_cls),
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
