import pytest
from quintus.evals.helpers import collect_required_attr, generate_filters
from .helpers import EvaluationTestAttrs


@pytest.mark.parametrize(
    ("attrs", "result"),
    [
        ([{"empty": {}}], {"empty": {}}),
        ([{"collect": {"0"}}, {"collect": {"1"}}], {"collect": {"0", "1"}}),
        ([{"summerize": {"0"}}, {"summerize": {"0"}}], {"summerize": {"0"}}),
        (
            [{"different0": {"0"}}, {"different1": {"0"}}],
            {"different0": {"0"}, "different1": {"0"}},
        ),
    ],
)
def test_collect_required_attr(attrs, result):
    evaluations = []
    for attr in attrs:
        evaluations.append(EvaluationTestAttrs(attr))
    sol = collect_required_attr(evaluations)
    assert sol == result


@pytest.mark.parametrize(
    ("required_attr", "result"),
    [({"exists": {}}, {"exists": {"$and": [{"usage": {"$in": ["exists"]}}]}})],
)
def test_generate_filters(required_attr, result):
    sol = generate_filters(required_attr)
    print(sol)
    assert sol == result
