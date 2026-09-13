from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc

from database.connection import get_db
from database import models
from schemas.sensor import SensorReadingIn, SensorReadingOut, LatestSensorsResponse, ParameterSummary
from services.threshold_service import get_thresholds, evaluate_status, build_alert_if_needed
from services.connection_manager import manager
from services.demo_generator import demo_generator
from services.system_settings import get_demo_mode
from config.settings import settings
from services.threshold_service import get_thresholds, evaluate_status, build_alert_if_needed, has_recent_active_alert
from services.reading_buffer import reading_buffer

router = APIRouter(prefix="/api/sensors", tags=["sensors"])

PARAM_UNITS = {"temperature": "°C", "current": "A", "vibration": "mm/s RMS", "rpm": "RPM"}

# A sensor is considered disconnected if no row has arrived in this long
STALE_AFTER_SECONDS = 15


@router.post("/data", status_code=201)
async def post_sensor_data(
    reading: SensorReadingIn,
    db: Session = Depends(get_db),
    x_device_api_key: Optional[str] = Header(default=None),
):
    """
    Endpoint the microcontroller (or any real sensor gateway) posts to.
    If DEVICE_API_KEY is set in .env, the header X-Device-Api-Key must match it.
    """
    if settings.api_key:
        if x_device_api_key != settings.api_key:
            raise HTTPException(status_code=401, detail="Invalid or missing X-Device-Api-Key header.")

    # Real hardware data arriving automatically takes priority - stop the demo generator.
    if reading.source == "real" and demo_generator.is_running():
        demo_generator.stop()

    row = models.SensorData(
        motor_id=reading.motor_id,
        temperature=reading.temperature,
        current=reading.current,
        vibration=reading.vibration,
        rpm=reading.rpm,
        source=reading.source,
        timestamp=reading.timestamp or datetime.now(timezone.utc),
    )
    db.add(row)
    db.commit()
    db.refresh(row)

    thresholds = get_thresholds(db)
    new_alerts = []
    values = {"temperature": reading.temperature, "current": reading.current,
              "vibration": reading.vibration, "rpm": reading.rpm}
    if all(v is not None for v in values.values()):
        reading_buffer.add(reading.motor_id, values)
    for param, value in values.items():
        if value is None:
            continue
        status = evaluate_status(param, value, thresholds)
        alert_data = build_alert_if_needed(param, value, status, thresholds)
        if alert_data and not has_recent_active_alert(db, reading.motor_id, param, status):
            alert = models.Alert(motor_id=reading.motor_id, **alert_data)
            db.add(alert)
            db.commit()
            db.refresh(alert)
            new_alerts.append({
                "id": alert.id, "parameter": alert.parameter,
                "severity": alert.severity, "message": alert.message,
                "timestamp": alert.timestamp.isoformat() if alert.timestamp else None,
            })

    await manager.broadcast({
        "type": "sensor_update",
        "demo_mode": False,
        "motor_id": reading.motor_id,
        "timestamp": row.timestamp.isoformat() if row.timestamp else datetime.now(timezone.utc).isoformat(),
        "data": values,
        "new_alerts": new_alerts,
    })

    return {"status": "ok", "id": row.id}


@router.get("/latest", response_model=LatestSensorsResponse)
def get_latest(db: Session = Depends(get_db)):
    latest_row = (
        db.query(models.SensorData)
        .filter(models.SensorData.motor_id == settings.motor_id)
        .order_by(desc(models.SensorData.timestamp))
        .first()
    )

    demo_mode = get_demo_mode(db)

    if not latest_row:
        params = [
            ParameterSummary(parameter=p, unit=PARAM_UNITS[p], value=None, status="NO_DATA",
                              trend="unknown", min_value=None, max_value=None,
                              last_updated=None, connected=False)
            for p in PARAM_UNITS
        ]
        return LatestSensorsResponse(motor_id=settings.motor_id, demo_mode=demo_mode, parameters=params)

    is_stale = (datetime.now(timezone.utc) - latest_row.timestamp.replace(tzinfo=timezone.utc)) \
        > timedelta(seconds=STALE_AFTER_SECONDS) if latest_row.timestamp else True

    thresholds = get_thresholds(db)

    # min/max over last 24h for each parameter
    window_start = datetime.now(timezone.utc) - timedelta(hours=24)
    recent_rows = (
        db.query(models.SensorData)
        .filter(models.SensorData.motor_id == settings.motor_id, models.SensorData.timestamp >= window_start)
        .order_by(asc(models.SensorData.timestamp))
        .all()
    )

    params = []
    for p in PARAM_UNITS:
        value = getattr(latest_row, p)
        connected = value is not None and not is_stale
        status = evaluate_status(p, value, thresholds) if connected else "NO_DATA"

        series = [getattr(r, p) for r in recent_rows if getattr(r, p) is not None]
        min_v = min(series) if series else None
        max_v = max(series) if series else None

        trend = "unknown"
        if len(series) >= 2:
            delta = series[-1] - series[-2]
            trend = "up" if delta > 0.01 else "down" if delta < -0.01 else "flat"

        params.append(ParameterSummary(
            parameter=p, unit=PARAM_UNITS[p], value=value if connected else None,
            status=status, trend=trend, min_value=min_v, max_value=max_v,
            last_updated=latest_row.timestamp, connected=connected,
        ))

    return LatestSensorsResponse(motor_id=settings.motor_id, demo_mode=demo_mode, parameters=params)


@router.get("/history", response_model=list[SensorReadingOut])
def get_history(
    range: str = "1h",
    parameter: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """range: one of 1m, 5m, 30m, 1h, 24h"""
    ranges = {"1m": 1, "5m": 5, "30m": 30, "1h": 60, "24h": 24 * 60}
    minutes = ranges.get(range, 60)
    window_start = datetime.now(timezone.utc) - timedelta(minutes=minutes)

    rows = (
        db.query(models.SensorData)
        .filter(models.SensorData.motor_id == settings.motor_id, models.SensorData.timestamp >= window_start)
        .order_by(asc(models.SensorData.timestamp))
        .all()
    )
    return rows
