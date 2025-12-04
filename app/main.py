# app/main.py
from fastapi import FastAPI
import os

app = FastAPI()
VERSION = os.getenv("MODEL_VERSION", "v1.0.0")

@app.get("/health")
def health():
    return {"status": "ok", "version": VERSION}

@app.get("/predict")
def predict():
    return {"prediction": "ok", "version": VERSION}