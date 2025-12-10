import logging
import os

from fastapi import FastAPI
from pydantic import BaseModel

from .model import load_model

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ml-service")

app = FastAPI(title="ML Service", version="1.0.0")

MODEL_VERSION = os.getenv("MODEL_VERSION", "v1.0.0")
model = load_model()


class PredictRequest(BaseModel):
    x: list[float]


class PredictResponse(BaseModel):
    prediction: float
    model_version: str


@app.get("/health")
def health():
    logger.info("Health check requested", extra={"model_version": MODEL_VERSION})
    return {
        "status": "ok",
        "version": MODEL_VERSION,
    }


@app.post("/predict", response_model=PredictResponse)
def predict(data: PredictRequest):
    prediction = float(model(data.x))
    logger.info(
        "Prediction made",
        extra={
            "model_version": MODEL_VERSION,
            "input_len": len(data.x),
            "prediction": prediction,
        },
    )
    return PredictResponse(prediction=prediction, model_version=MODEL_VERSION)
