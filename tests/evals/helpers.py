from quintus.evals.evaluation import Evaluation


class EvaluationTestAttrs(Evaluation):
    def __init__(self, attrs: dict[str, set[str]]):
        self.required_attrs = attrs

    def get_required_attrs(self) -> dict[str, set[str]]:
        return self.required_attrs

    def evaluate(self, **kwargs) -> float:
        return 0.0
