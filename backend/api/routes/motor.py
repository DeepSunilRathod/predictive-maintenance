from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc

from database.connection import get_db
from database import models
from schemas.motor import MotorInfoOut, MotorStatusOut
from services.demo_generator import demo_generator
from services.system_settings import get_demo_mode
from config.settings import settings

router = APIRouter(prefix="/api/motor", tags=["motor"])

STALE_AFTER_SECONDS = 15


@router.get("/status", response_model=MotorStatusOut)
def get_status(db: Session = Depends(get_db)):
    latest = (
        db.query(models.SensorData)
        .filter(models.SensorData.motor_id == settings.motor_id)
        .order_by(desc(models.SensorData.timestamp))
        .first()
    )
    demo_mode = get_demo_mode(db)

    if not latest:
        return MotorStatusOut(
            motor_id=settings.motor_id, connection_status="DISCONNECTED",
            demo_mode=demo_mode, last_updated=None, system_status="OFFLINE",
        )

    is_stale = (datetime.now(timezone.utc) - latest.timestamp.replace(tzinfo=timezone.utc)) \
        > timedelta(seconds=STALE_AFTER_SECONDS)

    if is_stale:
        connection_status = "DISCONNECTED"
        system_status = "OFFLINE"
    elif latest.source == "demo":
        connection_status = "DEMO"
        system_status = "OK"
    else:
        connection_status = "CONNECTED"
        system_status = "OK"

    return MotorStatusOut(
        motor_id=settings.motor_id, connection_status=connection_status,
        demo_mode=demo_mode, last_updated=latest.timestamp, system_status=system_status,
    )


@router.get("/details", response_model=MotorInfoOut)
def get_details(db: Session = Depends(get_db)):
    motor = db.query(models.MotorInfo).filter_by(motor_id=settings.motor_id).first()
    if not motor:
        raise HTTPException(status_code=404, detail="Motor info not configured yet.")
    return motor


@router.put("/details", response_model=MotorInfoOut)
def update_details(payload: MotorInfoOut, db: Session = Depends(get_db)):
    motor = db.query(models.MotorInfo).filter_by(motor_id=settings.motor_id).first()
    if not motor:
        motor = models.MotorInfo(motor_id=settings.motor_id)
        db.add(motor)
    motor.motor_type = payload.motor_type
    motor.rated_voltage = payload.rated_voltage
    motor.rated_power_kw = payload.rated_power_kw
    motor.rated_rpm = payload.rated_rpm
    motor.installation_date = payload.installation_date
    motor.total_operating_hours = payload.total_operating_hours
    db.commit()
    db.refresh(motor)
    return motor
