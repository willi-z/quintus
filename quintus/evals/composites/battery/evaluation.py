from abc import abstractmethod
from quintus.evals import BasicEvaluation
from quintus.structures.component import Component
from quintus.structures.helpers import component_to_filter


def convert(cls: Component | None, **kwargs):
    if cls is None:
        return None
    else:
        return cls.__class__(**kwargs)


class BatteryEvaluation(BasicEvaluation):
    def __init__(
        self,
        name: str,
        unit: str | None,
        anode: Component = None,
        cathode: Component = None,
        foil: Component = None,
        separator: Component = None,
    ):
        self.anode_cls = anode
        self.cathode_cls = cathode
        self.foil_cls = foil
        self.separator_cls = separator

        super().__init__(
            name,
            unit,
            {
                "anode": component_to_filter(self.anode_cls),
                "cathode": component_to_filter(self.cathode_cls),
                "foil": component_to_filter(self.foil_cls),
                "separator": component_to_filter(self.separator_cls),
            },
        )

    @abstractmethod
    def compute_battery(
        self,
        anode: Component,
        cathode: Component,
        foil: Component,
        separator: Component,
    ) -> float:
        pass

    def __compute__(self, **kwargs) -> float:
        anode = convert(self.anode_cls, **kwargs["anode"])
        cathode = convert(self.cathode_cls, **kwargs["cathode"])
        foil = convert(self.foil_cls, **kwargs["foil"])
        separator = convert(self.separator_cls, **kwargs["separator"])
        return self.compute_battery(anode, cathode, foil, separator)
