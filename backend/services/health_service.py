"""
Rule-based Motor Health Score.

Explicitly NOT an ML prediction - this is a transparent, explainable score
computed from how close the four live parameters are to their configured
thresholds. It exists so the dashboard has *something* honest to show before
a trained ML model is available. See ml/predict.py for the ML-based path,
which is kept separate and clearly labeled.
"""
from typing import Optional
from services.threshold_service import evaluate_status

STATUS_PENALTY = {"NORMAL": 0, "WARNING": 15, "CRITICAL": 35, "NO_DATA": 10}


def compute_health_score(readings: dict, thresholds: dict) -> tuple[Optional[float], str, str]:
    """
    readings: {"temperature": val, "current": val, "vibration": val, "rpm": val}
    Returns (score 0-100 or None, status GOOD/WARNING/CRITICAL/UNKNOWN, basis string)
    """
    if all(v is None for v in readings.values()):
        return None, "UNKNOWN", "No sensor data available yet."

    score = 100.0
    worst_status = "NORMAL"
    order = {"NORMAL": 0, "WARNING": 1, "CRITICAL": 2, "NO_DATA": 0}

    for param, value in readings.items():
        status = evaluate_status(param, value, thresholds)
        score -= STATUS_PENALTY[status]
        if order[status] > order[worst_status]:
            worst_status = status

    score = max(0.0, min(100.0, score))

    if worst_status == "CRITICAL":
        health_status = "CRITICAL"
    elif worst_status == "WARNING":
        health_status = "WARNING"
    else:
        health_status = "GOOD"

    basis = (
        "Rule-based score: 100 minus a penalty for each parameter currently in "
        "WARNING (-15) or CRITICAL (-35) relative to its configured threshold. "
        "This is not an ML prediction."
    )
    return round(score, 1), health_status, basis
