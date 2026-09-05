"""
Inference wrapper used by the /api/predict endpoint.

If ml/model.pkl does not exist (i.e. train_model.py has never been run
against a real labeled dataset), this module honestly reports that no
model is available instead of fabricating a prediction. The API
(schemas/predict.py -> PredictOut) is shaped so the frontend can render
either outcome without special-casing.
"""
import os
from datetime import datetime, timezone
import joblib

from ml.preprocessing import to_feature_vector, validate_reading, FEATURE_ORDER

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")

_cached = None
_cache_loaded = False


def _load_model():
    global _cached, _cache_loaded
    if _cache_loaded:
        return _cached
    _cache_loaded = True
    if os.path.exists(MODEL_PATH):
        _cached = joblib.load(MODEL_PATH)
    else:
        _cached = None
    return _cached


def is_model_available() -> bool:
    return _load_model() is not None


def predict(reading: dict) -> dict:
    """
    reading: {"temperature": .., "current": .., "vibration": .., "rpm": ..}
    Returns a dict matching schemas.predict.PredictOut fields.
    """
    now = datetime.now(timezone.utc)
    problems = validate_reading(reading)
    if problems:
        return {
            "model_available": is_model_available(),
            "status": "INVALID_INPUT",
            "failure_probability": None,
            "predicted_condition": None,
            "confidence": None,
            "remaining_useful_life_hours": None,
            "note": "; ".join(problems),
            "prediction_timestamp": now,
        }

    bundle = _load_model()
    if bundle is None:
        return {
            "model_available": False,
            "status": "MODEL_NOT_AVAILABLE",
            "failure_probability": None,
            "predicted_condition": None,
            "confidence": None,
            "remaining_useful_life_hours": None,  # RUL requires a separate, currently unbuilt, regression model
            "note": (
                "No trained fault-classification model is available yet. Train one via "
                "ml/train_model.py once real labeled data exists (see ml/data/README.md). "
                "Remaining Useful Life (RUL) additionally requires a separate regression "
                "model trained on run-to-failure data, which is not implemented."
            ),
            "prediction_timestamp": now,
        }

    model = bundle["model"]
    X = to_feature_vector(reading)
    pred_class = model.predict(X)[0]

    confidence = None
    failure_probability = None
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(X)[0]
        classes = list(model.classes_)
        confidence = float(max(proba))
        if "Normal" in classes:
            normal_idx = classes.index("Normal")
            failure_probability = float(1 - proba[normal_idx])
        else:
            failure_probability = float(1 - confidence)

    status = "NORMAL" if pred_class == "Normal" else "WARNING"

    return {
        "model_available": True,
        "status": status,
        "failure_probability": round(failure_probability, 3) if failure_probability is not None else None,
        "predicted_condition": str(pred_class),
        "confidence": round(confidence, 3) if confidence is not None else None,
        "remaining_useful_life_hours": None,  # not implemented - see note
        "note": (
            f"Prediction from trained model (held-out test accuracy at training time: "
            f"{bundle.get('test_accuracy', 'unknown')}). RUL is not implemented - a separate "
            f"regression model on run-to-failure data would be required."
        ),
        "prediction_timestamp": now,
    }
