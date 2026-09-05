from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc

from database.connection import get_db
from database import models
from schemas.health import HealthOut
from services.threshold_service import get_thresholds
from services.health_service import compute_health_score
from config.settings import settings

router = APIRouter(prefix="/api/health", tags=["health"])


@router.get("", response_model=HealthOut)
def get_health(db: Session = Depends(get_db)):
    latest = (
        db.query(models.SensorData)
        .filter(models.SensorData.motor_id == settings.motor_id)
        .order_by(desc(models.SensorData.timestamp))
        .first()
    )
    thresholds = get_thresholds(db)

    readings = {
        "temperature": latest.temperature if latest else None,
        "current": latest.current if latest else None,
        "vibration": latest.vibration if latest else None,
        "rpm": latest.rpm if latest else None,
    }
    score, status, basis = compute_health_score(readings, thresholds)

    last_alert = (
        db.query(models.Alert)
        .filter(models.Alert.motor_id == settings.motor_id)
        .order_by(desc(models.Alert.timestamp))
        .first()
    )

    motor = db.query(models.MotorInfo).filter_by(motor_id=settings.motor_id).first()
    operating_hours = motor.total_operating_hours if motor else 0.0

    risk_level = {"GOOD": "LOW", "WARNING": "MEDIUM", "CRITICAL": "HIGH", "UNKNOWN": "UNKNOWN"}[status]
    action = {
        "GOOD": "No action required - continue normal operation and routine monitoring.",
        "WARNING": "Schedule an inspection soon; monitor the flagged parameter closely.",
        "CRITICAL": "Inspect immediately and consider taking the motor offline until resolved.",
        "UNKNOWN": "Insufficient sensor data to assess health - check sensor connections.",
    }[status]

    return HealthOut(
        motor_id=settings.motor_id,
        health_score=score,
        status=status,
        risk_level=risk_level,
        recommended_action=action,
        last_fault_detected=last_alert.message if last_alert else None,
        last_fault_timestamp=last_alert.timestamp if last_alert else None,
        operating_hours=operating_hours,
        basis=basis,
    )
