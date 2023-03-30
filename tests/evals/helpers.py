from quintus.evals.evaluation import BasicEvaluation


class EvaluationTestAttrs(BasicEvaluation):
    def __init__(self, attrs: dict[str, dict]):
        super().__init__("TestAttrs", None, attrs)

    def compute(self, **kwargs) -> float:
        return 0.0
