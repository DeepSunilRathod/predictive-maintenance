"""
Inference wrapper for the trained CNN+LSTM fault-classification model.
"""
import os
from datetime import datetime, timezone
import numpy as np
import joblib
from tensorflow import keras

MODEL_PATH = os.path.join(os.path.dirname(__file__), "motor_cnn_lstm.keras")
SCALER_PATH = os.path.join(os.path.dirname(__file__), "feature_scaler.joblib")
LABEL_ENCODER_PATH = os.path.join(os.path.dirname(__file__), "label_encoder.joblib")

RATED_VOLTAGE = 230.0
ASSUMED_POWER_FACTOR = 0.85

_model = None
_scaler = None
_label_encoder = None
_loaded = False


def _load():
    global _model, _scaler, _label_encoder, _loaded
    if _loaded:
        return
    _loaded = True
    if os.path.exists(MODEL_PATH):
        _model = keras.models.load_model(MODEL_PATH)
        _scaler = joblib.load(SCALER_PATH)
        _label_encoder = joblib.load(LABEL_ENCODER_PATH)


def is_model_available() -> bool:
    _load()
    return _model is not None


def approximate_power_torque(current: float, rpm: float) -> tuple[float, float]:
    power_kw = (3 ** 0.5) * RATED_VOLTAGE * current * ASSUMED_POWER_FACTOR / 1000.0
    torque = (power_kw * 9550.0 / rpm) if rpm and rpm > 0 else 0.0
    return power_kw, torque


def window_to_array(window: list[dict]) -> np.ndarray:
    rows = []
    for r in window:
        power, torque = approximate_power_torque(r["current"], r["rpm"])
        rows.append([r["rpm"], r["vibration"], torque, power, r["current"]])
    return np.array(rows, dtype=np.float32)


def predict_from_window(window: list[dict]) -> dict:
    now = datetime.now(timezone.utc)
    _load()

    if _model is None:
        return {
            "model_available": False,
            "status": "MODEL_NOT_AVAILABLE",
            "failure_probability": None,
            "predicted_condition": None,
            "confidence": None,
            "remaining_useful_life_hours": None,
            "note": "Trained model files not found in backend/ml/.",
            "prediction_timestamp": now,
        }

    arr = window_to_array(window)
    scaled = _scaler.transform(arr).reshape(1, arr.shape[0], arr.shape[1])

    proba = _model.predict(scaled, verbose=0)[0]
    classes = list(_label_encoder.classes_)
    pred_idx = int(np.argmax(proba))
    predicted_condition = classes[pred_idx]
    confidence = float(proba[pred_idx])

    if "Normal" in classes:
        normal_idx = classes.index("Normal")
        failure_probability = float(1 - proba[normal_idx])
    else:
        failure_probability = float(1 - confidence)

    status = "NORMAL" if predicted_condition == "Normal" else "WARNING"

    return {
        "model_available": True,
        "status": status,
        "failure_probability": round(failure_probability, 3),
        "predicted_condition": predicted_condition,
        "confidence": round(confidence, 3),
        "remaining_useful_life_hours": None,
        "note": (
            "Prediction from CNN+LSTM model trained on simulated fault data (broken bearing, "
            "broken rotor bar, stator winding short, voltage imbalance, normal) across 7 motor "
            "power ratings, 99%+ held-out test accuracy. Power and Torque inputs are approximated "
            "from Current and RPM (assumed 230V, 0.85 power factor), not directly measured. "
            "RUL is not implemented."
        ),
        "prediction_timestamp": now,
    }