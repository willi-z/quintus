from .constants import CONST_F, NUM_ELECTRODE_LAYERS, OUTER_ELECTRODE_LAYER
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


def generate_layup_ids() -> list[str]:
    layup = ["foil"]
    for i in range(NUM_ELECTRODE_LAYERS):
        if OUTER_ELECTRODE_LAYER == "cathode":
            if i % 2 == 0:
                layup.append("cathode")
            else:
                layup.append("anode")
        else:
            if i % 2 == 0:
                layup.append("anode")
            else:
                layup.append("cathode")
        if i + 1 < NUM_ELECTRODE_LAYERS:
            layup.append("separator")
    layup.append("foil")
    return layup


def generate_layup(anode, cathode, foil, separator) -> list[Component]:
    ids = generate_layup_ids()
    layup = []
    for id in ids:
        if id == "anode":
            layup.append(anode)
        elif id == "cathode":
            layup.append(cathode)
        elif id == "foil":
            layup.append(foil)
        elif id == "separator":
            layup.append(separator)
        else:
            raise ValueError(f"Unknown layer id: {id}.")
    return layup
