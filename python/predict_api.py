from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import joblib

from pathlib import Path


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_DIR = BASE_DIR / "models"


# ============================================================
# LOAD MODEL
# ============================================================

model_path = MODEL_DIR / "logiopt_delay_model.pkl"
preprocessor_path = MODEL_DIR / "logiopt_preprocessor.pkl"

model = joblib.load(model_path)
preprocessor = joblib.load(preprocessor_path)


# ============================================================
# FASTAPI
# ============================================================

app = FastAPI(
    title="LogiOpt AI Prediction API",
    description="Shipment delay prediction API",
    version="1.0"
)


# ============================================================
# INPUT FORMAT
# ============================================================

class Shipment(BaseModel):

    Shipment_ID: str

    Distance_KM: float

    Carrier: str

    Vehicle_ID: str

    Load_KG: float

    Traffic: str

    Weather: str

    Priority: str

    Delivery_Window_Hours: float


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():

    return {
        "message": "LogiOpt AI Prediction API is running"
    }


# ============================================================
# PREDICT
# ============================================================

@app.post("/predict")
def predict(shipment: Shipment):

    # Convert request to DataFrame

    data = pd.DataFrame([{
        "Distance_KM": shipment.Distance_KM,
        "Carrier": shipment.Carrier,
        "Vehicle_ID": shipment.Vehicle_ID,
        "Load_KG": shipment.Load_KG,
        "Traffic": shipment.Traffic,
        "Weather": shipment.Weather,
        "Priority": shipment.Priority,
        "Delivery_Window_Hours": shipment.Delivery_Window_Hours
    }])


    # Apply preprocessing

    X = preprocessor.transform(data)


    # Predict probability

    probability = model.predict_proba(X)[0][1]


    # Risk classification

    if probability < 0.40:

        risk = "LOW"

    elif probability < 0.70:

        risk = "MEDIUM"

    else:

        risk = "HIGH"


    # Return result

    return {

        "shipment_id": shipment.Shipment_ID,

        "delay_probability": round(
            float(probability),
            4
        ),

        "delay_probability_percent": round(
            float(probability) * 100,
            2
        ),

        "risk_level": risk

    }