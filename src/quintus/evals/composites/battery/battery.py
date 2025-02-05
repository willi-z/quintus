from typing import Callable
from quintus.structures import Component
from quintus.composers import StackupComposer


class BatteryStackupComposer(StackupComposer):
    def __init__(self, num_electrodes: int, outer_electrode: str = "anode"):
        if not outer_electrode in {"anode", "cathode"}:
            raise RuntimeError(f"outer_electrode option can only be 'anode' or 'cathode', but found: {outer_electrode}!")
        self.outer_electrode = outer_electrode
        super().__init__(num_electrodes, self.battery_stackup_definition)

    def is_compatible_with(self, component_key: str) -> bool:
        return component_key in {"anode", "cathode", "separator", "foil", "electrolyte"}
    
    def battery_stackup_definition(self, num_electrodes: int) -> list[str]:
        layup = ["foil"]
        for i in range(num_electrodes):
            if self.outer_electrode == "cathode":
                if i % 2 == 0:
                    layup.append("cathode")
                else:
                    layup.append("anode")
            else:
                if i % 2 == 0:
                    layup.append("anode")
                else:
                    layup.append("cathode")
            if i + 1 < num_electrodes:
                layup.append("separator")
        layup.append("foil")
        return layup
    

class Battery(Component):
    def __init__(self, **kwargs):
        super(**kwargs)

    def get_anode(self) -> Component | None:
        return self.composition.components.get("anode")

    def get_cathode(self) -> Component | None:
        return self.composition.components.get("cathode")

    def get_separator(self) -> Component | None:
        return self.composition.components.get("separator")

    def get_electrolyte(self) -> Component | None:
        return self.composition.components.get("electrolyte")

    def get_stackup(self) -> list[str]:
        return self.composition.options["stackup"]