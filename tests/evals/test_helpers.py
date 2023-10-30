import pytest
from quintus.evals import generate_filters
from .helpers import EvaluationTestAttrs


@pytest.mark.parametrize(
    ("attrs", "result"),
    [
        ([{"empty": {"$and": [{}]}}], {"empty": {"$and": [{}]}}),
        (
            [{"collect": {"$and": [{"0"}]}}, {"collect": {"$and": [{"1"}]}}],
            {"collect": {"$and": [{"0"}, {"1"}]}},
        ),
        (
            [{"summerize": {"$and": [{"0"}]}}, {"summerize": {"$and": [{"0"}]}}],
            {"summerize": {"$and": [{"0"}, {"0"}]}},
        ),
        (
            [{"different0": {"$and": [{"0"}]}}, {"different1": {"$and": [{"0"}]}}],
            {"different0": {"$and": [{"0"}]}, "different1": {"$and": [{"0"}]}},
        ),
    ],
)
def test_generate_filters(attrs: dict[str, dict], result: dict[str, list]):
    evaluations = []
    for attr in attrs:
        evaluations.append(EvaluationTestAttrs(attr))
    sol = generate_filters(evaluations)
    assert sol == result
