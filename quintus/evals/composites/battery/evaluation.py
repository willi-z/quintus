from abc import abstractmethod
from quintus.evals import BasicEvaluation
from pydantic import BaseModel
from quintus.structures.component import Component
from typing import Type


def generate_attribute_filter(cls: Type[BaseModel] | None) -> dict:
    """_summary_

    Parameters
    ----------
    cls : Type[BaseModel] | None
        _description_

    Returns
    -------
    dict
        filter using the query system from MongoDB
        (see: https://www.mongodb.com/docs/manual/tutorial/query-documents/)
    """
    if cls is None:
        return None
    else:
        attr_filter = []

        for attr, field in cls.__fields__.items():
            if field is not None:
                {attr: generate_attribute_filter(field)}
            else:
                attr_filter.append({attr: {"$exists": True}})
    return {"$and": attr_filter}


def convert(cls: Type[BaseModel] | None, **kwargs):
    if cls is None:
        return None
    else:
        return cls(**kwargs)


class BatteryEvaluation(BasicEvaluation):
    def __init__(
        self,
        name: str,
        unit: str | None,
        anode_cls: Type[Component] = None,
        cathode_cls: Type[Component] = None,
        foil_cls: Type[Component] = None,
        separator_cls: Type[Component] = None,
    ):
        self.anode_cls = anode_cls
        self.cathode_cls = cathode_cls
        self.foil_cls = foil_cls
        self.separator_cls = separator_cls

        super().__init__(
            name,
            unit,
            {
                "anode": generate_attribute_filter(self.anode_cls),
                "cathode": generate_attribute_filter(self.cathode_cls),
                "foil": generate_attribute_filter(self.foil_cls),
                "separator": generate_attribute_filter(self.separator_cls),
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
