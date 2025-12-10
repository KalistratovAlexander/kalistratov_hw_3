import pickle
from pathlib import Path
from typing import Any

MODEL_PATH = Path(__file__).parent / "model.pkl"


def load_model() -> Any:
    if MODEL_PATH.exists():
        with open(MODEL_PATH, "rb") as f:
            model = pickle.load(f)
    else:
        # Заглушка: простая "модель", суммирующая вход
        def model_stub(xs):
            return sum(xs)

        model = model_stub
    return model