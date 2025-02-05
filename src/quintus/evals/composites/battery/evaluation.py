from abc import abstractmethod
from .battery import Battery
from quintus.evals import BasicEvaluation
from quintus.structures import Component, Measurement
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
        required_measurements: set[str] = None,
        anode: Component = None,
        cathode: Component = None,
        foil: Component = None,
        separator: Component = None,
        electrolyte: Component = None,
        inlude_only_taged: bool = True,
    ):
        self.anode_cls = anode
        self.cathode_cls = cathode
        self.foil_cls = foil
        self.separator_cls = separator
        self.electrolyte_cls = electrolyte

        component_filters = {
            "anode": component_to_filter(self.anode_cls),
            "cathode": component_to_filter(self.cathode_cls),
            "foil": component_to_filter(self.foil_cls),
            "separator": component_to_filter(self.separator_cls),
            "electrolyte": component_to_filter(self.electrolyte_cls),
        }

        if inlude_only_taged:
            for key, item in component_filters.items():
                item["tags"] = key

        super().__init__(name, unit, required_measurements, component_filters)

    @abstractmethod
    def compute_battery(
        self,
        battery: Battery
    ) -> float:
        pass

    def __compute__(self, component: Component) -> float:
        component.__class__ = Battery
        return self.compute_battery( 
            component
        )
