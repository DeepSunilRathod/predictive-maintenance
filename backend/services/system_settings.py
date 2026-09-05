"""Small helper for reading/writing runtime toggles stored in system_settings."""
from sqlalchemy.orm import Session
from database import models


def get_demo_mode(db: Session) -> bool:
    row = db.query(models.SystemSetting).filter_by(key="demo_mode").first()
    if not row:
        return True
    return row.value.lower() == "true"


def set_demo_mode(db: Session, value: bool) -> None:
    row = db.query(models.SystemSetting).filter_by(key="demo_mode").first()
    if not row:
        row = models.SystemSetting(key="demo_mode", value=str(value).lower())
        db.add(row)
    else:
        row.value = str(value).lower()
    db.commit()
