from quintus.evals.evaluation import Evaluation


class EvaluationTestAttrs(Evaluation):
    def __init__(self, attrs: dict[str, dict]):
        self.required_attrs = attrs

    def filter_per_args(self) -> dict[str, dict]:
        return self.required_attrs

    def evaluate(self, **kwargs) -> float:
        return 0.0
