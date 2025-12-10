import pickle
from pathlib import Path
from typing import Any, Iterable, List

MODEL_PATH = Path(__file__).parent / "model.pkl"


class LinearModel:
    def __init__(self, weights: List[float], bias: float) -> None:
        self.weights = list(weights)
        self.bias = bias

    def __call__(self, xs: Iterable[float]) -> float:
        return sum(w * x for w, x in zip(self.weights, xs)) + self.bias


def load_model() -> Any:
    if MODEL_PATH.exists():
        with open(MODEL_PATH, "rb") as f:
            data = pickle.load(f)

        if isinstance(data, dict) and "weights" in data and "bias" in data:
            return LinearModel(weights=data["weights"], bias=data["bias"])

        return data
