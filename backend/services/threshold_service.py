"""
Rule-based threshold evaluation.

This is deliberately simple and explainable: a parameter's status is derived
by comparing its latest value against the configured thresholds (from the DB,
seeded from config/thresholds.py). This is NOT the ML model - see ml/predict.py
for the separate, clearly-labeled predictive path.
"""
import json
from typing import Optional
from sqlalchemy.orm import Session

from database import models


def get_thresholds(db: Session) -> dict:
    rows = db.query(models.Threshold).all()
    result = {}
    for row in rows:
        extra = json.loads(row.extra_json) if row.extra_json else {}
        result[row.parameter] = {
            "unit": row.unit,
            "normal_max": row.normal_max,
            "warning_max": row.warning_max,
            "critical_max": row.critical_max,
            **{k: v for k, v in extra.items() if k not in ("unit", "normal_max", "warning_max", "critical_max")},
        }
    return result


def evaluate_status(parameter: str, value: Optional[float], thresholds: dict) -> str:
    """Returns NORMAL | WARNING | CRITICAL | NO_DATA."""
    if value is None:
        return "NO_DATA"
    cfg = thresholds.get(parameter)
    if not cfg:
        return "NORMAL"

    if parameter == "rpm":
        rated = cfg.get("rated")
        if not rated:
            return "NORMAL"
        deviation_pct = abs(value - rated) / rated * 100
        if deviation_pct <= cfg.get("normal_band_pct", 5):
            return "NORMAL"
        elif deviation_pct <= cfg.get("warning_band_pct", 10):
            return "WARNING"
        elif deviation_pct <= cfg.get("critical_band_pct", 20):
            return "CRITICAL"
        else:
            return "CRITICAL"

    critical_max = cfg.get("critical_max")
    warning_max = cfg.get("warning_max")
    normal_max = cfg.get("normal_max")

    if critical_max is not None and value >= critical_max:
        return "CRITICAL"
    if warning_max is not None and value >= warning_max:
        return "WARNING"
    if normal_max is not None and value >= normal_max:
        return "WARNING"
    return "NORMAL"


def build_alert_if_needed(parameter: str, value: float, status: str, thresholds: dict) -> Optional[dict]:
    """Returns an alert dict (ready to persist) if status warrants one, else None."""
    if status not in ("WARNING", "CRITICAL"):
        return None

    cfg = thresholds.get(parameter, {})
    unit = cfg.get("unit", "")

    causes = {
        "temperature": "Motor overheating - possible excessive load, blocked ventilation, or cooling fan failure.",
        "current": "Overcurrent - possible mechanical overload, bearing friction, or supply voltage imbalance.",
        "vibration": "Excessive vibration - possible bearing wear, misalignment, imbalance, or looseness.",
        "rpm": "Speed deviation - possible load change, supply frequency issue, or mechanical fault.",
    }
    actions = {
        "temperature": "Inspect motor load and cooling/ventilation; verify ambient temperature.",
        "current": "Check for mechanical binding, verify supply voltage balance, inspect load.",
        "vibration": "Inspect bearings, coupling alignment, and mounting; consider vibration analysis.",
        "rpm": "Check load conditions and supply frequency; inspect for mechanical faults.",
    }

    threshold_value = (
        cfg.get("critical_max") if status == "CRITICAL" and cfg.get("critical_max") is not None
        else cfg.get("warning_max") if cfg.get("warning_max") is not None
        else cfg.get("normal_max")
    )
    if threshold_value is None:
        threshold_value = cfg.get("rated", value)

    return {
        "parameter": parameter,
        "value": value,
        "threshold": threshold_value,
        "severity": status,
        "message": f"{parameter.capitalize()} reading of {value}{unit} crossed the {status.lower()} threshold.",
        "possible_cause": causes.get(parameter),
        "recommended_action": actions.get(parameter),
    }
    

from datetime import datetime, timedelta

def has_recent_active_alert(db, motor_id: str, parameter: str, severity: str, cooldown_seconds: int = 120) -> bool:
    """True if an ACTIVE alert for this parameter/severity was already raised
    within the cooldown window, so we don't spam a new row every reading."""
    from database import models  # local import to avoid circulars
    cutoff = datetime.utcnow() - timedelta(seconds=cooldown_seconds)
    existing = (
        db.query(models.Alert)
        .filter(
            models.Alert.motor_id == motor_id,
            models.Alert.parameter == parameter,
            models.Alert.severity == severity,
            models.Alert.status == "ACTIVE",
            models.Alert.timestamp >= cutoff,
        )
        .first()
    )
    return existing is not None    
