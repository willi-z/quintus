from quintus.evals.battery import BatteryEvaluation
from quintus.structures import Material, get_SI_value
from quintus.evals.battery.helpers import get_active_layer


class ElectrodeCapacityCalc(BatteryEvaluation):
    def __init__(self):
        self.identifier = ""

        layers_filter = {
            "layers": {
                "$in": {
                    "$and": [
                        {"description": {"$eq": "active layer"}},
                        {"areal_capacity": {"$exists": True}},
                    ]
                }
            }
        }

        filters = {
            self.identifier: {
                "$and": [layers_filter, {"areal_capacity": {"$exists": False}}]
            }
        }
        super().__init__("areal_capacity", "C/m^2", filters, False)

    def compute(self, **kwargs) -> float:
        electrode = Material(kwargs[self.identifier])
        active_layer = get_active_layer(electrode)
        areal_capacity = active_layer.__fields__.get()
        return get_SI_value(areal_capacity)
