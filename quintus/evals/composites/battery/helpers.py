from .constants import CONST_F
from quintus.structures import Component


def calc_spec_capacity(n_el: int, molar_mass: float) -> float:
    """Calculate the specific capacity.
    Unit is [A s / <mass unit>]

    Args:
        n_el (int): number of electrones that are exchanged (Unit: [])
        molar_mass (float): molar mass (Unit [mol/<mass unit>])

    Returns:
        float: specific capacity
    """
    return n_el * CONST_F / molar_mass


def calc_spec_energy_density(spec_capacity: float, V_0: float) -> float:
    """Calculate the specific energy density. Unit is [W <time unit> / <mass unit>]

    Args:
        spec_capacity (float): specific capacity (Unit [A <time unit>/<mass unit>])
        V_0 (float): (standard) potential (Unit [V])

    Returns:
        float: specific energy density
    """
    assert spec_capacity >= 0
    return spec_capacity * abs(V_0)


def get_active_layer(material: Component) -> Component | None:
    if (comp := material.composition) is not None:
        if (layer := comp.get("active layer")) is not None:
            return layer
    return None
