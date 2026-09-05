"""
Feature preprocessing shared by train_model.py and predict.py.
Keeping this in one place guarantees train-time and inference-time
preprocessing never drift apart.
"""
import numpy as np

FEATURE_ORDER = ["temperature", "current", "vibration", "rpm"]


def to_feature_vector(reading: dict) -> np.ndarray:
    """Converts a {temperature, current, vibration, rpm} dict into the
    fixed-order numpy vector the model expects."""
    return np.array([[reading[f] for f in FEATURE_ORDER]], dtype=float)


def validate_reading(reading: dict) -> list[str]:
    """Basic sanity checks. Returns a list of problem strings (empty = OK)."""
    problems = []
    for f in FEATURE_ORDER:
        if f not in reading or reading[f] is None:
            problems.append(f"Missing required feature: {f}")
    if "current" in reading and reading.get("current") is not None and reading["current"] < 0:
        problems.append("current cannot be negative")
    if "rpm" in reading and reading.get("rpm") is not None and reading["rpm"] < 0:
        problems.append("rpm cannot be negative")
    return problems
