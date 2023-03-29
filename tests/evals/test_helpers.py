import pytest
from quintus.evals import generate_filters
from .helpers import EvaluationTestAttrs


@pytest.mark.parametrize(
    ("attrs", "result"),
    [
        ([{"empty": {}}], {"empty": [{}]}),
        ([{"collect": {"0"}}, {"collect": {"1"}}], {"collect": [{"0"}, {"1"}]}),
        ([{"summerize": {"0"}}, {"summerize": {"0"}}], {"summerize": [{"0"}, {"0"}]}),
        (
            [{"different0": {"0"}}, {"different1": {"0"}}],
            {"different0": [{"0"}], "different1": [{"0"}]},
        ),
    ],
)
def test_generate_filters(attrs: dict[str, dict], result: dict[str, list]):
    evaluations = []
    for attr in attrs:
        evaluations.append(EvaluationTestAttrs(attr))
    sol = generate_filters(evaluations)
    assert len(sol.keys()) == len(result.keys())
    for key in result.keys():
        assert key in sol.keys()
        res = sol[key]["$and"]
        assert res == result[key]
