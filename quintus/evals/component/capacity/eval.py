from quintus.evals.evaluation import BasicEvaluation
from quintus.structures import Component, get_SI_value, Measurement
from quintus.evals.composites.battery.helpers import get_active_layer


class ElectrodeCapacityCalc(BasicEvaluation):
    def __init__(self):
        raise NotImplementedError()
        """
        name = "areal_capacity"

        layers_filter = {
            "composites": {"active layer": {"areal_capacity": {"$exists": True}}}
        }

        filters = {name: layers_filter}
        super().__init__(name, "C/m^2", filters)
        """

    def __compute__(self, **kwargs) -> float:
        electrode = Component(**kwargs[self.name])
        active_layer = get_active_layer(electrode)
        areal_capacity = Measurement(**active_layer.__dict__.get("areal_capacity"))
        return get_SI_value(areal_capacity)
