from .constants import CONST_F
from quintus.structures import Layer, Material


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


def get_active_layer(material: Material) -> Layer | None:
    if material.layers is None:
        return None
    for i in range(len(material.layers)):
        layer = material.layers[i]
        descr = layer.__dict__.get("description")
        if descr is not None:
            if descr == "active layer":
                return layer

    return None
