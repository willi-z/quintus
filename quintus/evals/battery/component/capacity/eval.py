from quintus.evals.battery import BatteryEvaluation
from quintus.structures import Material, get_SI_value, Measurement
from quintus.evals.battery.helpers import get_active_layer


class ElectrodeCapacityCalc(BatteryEvaluation):
    def __init__(self):
        name = "areal_capacity"

        layers_filter = {
            "layers": {
                "$elemMatch": {
                    "description": {"$eq": "active layer"},
                    "areal_capacity": {"$exists": True},
                }
            }
        }

        filters = {name: layers_filter}
        super().__init__(name, "C/m^2", filters, False)

    def compute(self, **kwargs) -> float:
        electrode = Material(**kwargs[self.name])
        active_layer = get_active_layer(electrode)
        areal_capacity = Measurement(**active_layer.__dict__.get("areal_capacity"))
        return get_SI_value(areal_capacity)
