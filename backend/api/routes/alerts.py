from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc

from database.connection import get_db
from database import models
from schemas.alert import AlertOut
from config.settings import settings

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("", response_model=list[AlertOut])
def list_alerts(
    severity: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    q = db.query(models.Alert).filter(models.Alert.motor_id == settings.motor_id)
    if severity:
        q = q.filter(models.Alert.severity == severity.upper())
    if status:
        q = q.filter(models.Alert.status == status.upper())
    q = q.order_by(desc(models.Alert.timestamp)).limit(limit)
    return q.all()


@router.post("/{alert_id}/acknowledge", response_model=AlertOut)
def acknowledge_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if not alert:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.status = "ACKNOWLEDGED"
    db.commit()
    db.refresh(alert)
    return alert


@router.post("/{alert_id}/resolve", response_model=AlertOut)
def resolve_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if not alert:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.status = "RESOLVED"
    db.commit()
    db.refresh(alert)
    return alert
