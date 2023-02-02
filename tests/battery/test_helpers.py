import pytest

from quintus.battery.helpers import calc_spec_capacity, calc_spec_energy_density


@pytest.mark.parametrize("n_el, molar_mass, result", [(1, 6.940e-3, 3861.9)])
def test_calc_spec_capacity(n_el: int, molar_mass: float, result: float):
    assert round(calc_spec_capacity(n_el, molar_mass) / 3600, 1) == result


@pytest.mark.parametrize("spec_capacity, V_0, result", [(3861.885, -3.04, 11740.1)])
def test_calc_spec_energy_density(spec_capacity: float, V_0: float, result: float):
    assert round(calc_spec_energy_density(spec_capacity, V_0), 1) == result
