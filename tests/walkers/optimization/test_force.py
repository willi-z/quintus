import pytest
from quintus.walkers.optimization.force import (
    calc_config_indeces,
)  # , BruteForceOptimizer


@pytest.mark.parametrize(
    ("index", "sizes", "result"),
    [
        (0, [3, 2, 4], [0, 0, 0]),
        (2, [3, 2, 4], [2, 0, 0]),
        (3, [3, 2, 4], [0, 1, 0]),
        (5, [3, 2, 4], [2, 1, 0]),
        (6, [3, 2, 4], [0, 0, 1]),
    ],
)
def test_calc_config_indeces(index, sizes, result):
    indeces = calc_config_indeces(index, sizes)
    assert indeces == result
