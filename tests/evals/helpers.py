from quintus.evals.evaluation import BasicEvaluation


class EvaluationTestAttrs(BasicEvaluation):
    def __init__(self, attrs: dict[str, dict]):
        self.required_attrs = attrs

    def filter_per_args(self) -> dict[str, dict]:
        return self.required_attrs

    def compute(self, **kwargs) -> float:
        return 0.0
