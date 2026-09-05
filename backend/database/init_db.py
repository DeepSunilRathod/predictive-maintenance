"""
Creates all tables from the SQLAlchemy models and seeds default thresholds.

Usage:
    cd backend
    python -m database.init_db
"""
import json
from database.connection import engine, SessionLocal, Base
from database import models
from config.thresholds import DEFAULT_THRESHOLDS
from config.settings import settings


def run():
    print(f"Connecting to: {settings.db_host}:{settings.db_port}/{settings.db_name}")
    Base.metadata.create_all(bind=engine)
    print("Tables created (or already existed).")

    db = SessionLocal()
    try:
        # Seed thresholds table only if empty, so we never clobber values
        # you've since tuned to your real motor.
        existing = db.query(models.Threshold).count()
        if existing == 0:
            for param, cfg in DEFAULT_THRESHOLDS.items():
                row = models.Threshold(
                    parameter=param,
                    unit=cfg.get("unit", ""),
                    normal_max=cfg.get("normal_max"),
                    warning_max=cfg.get("warning_max"),
                    critical_max=cfg.get("critical_max"),
                    extra_json=json.dumps(cfg),
                    source_note=cfg.get("source"),
                )
                db.add(row)
            db.commit()
            print(f"Seeded {len(DEFAULT_THRESHOLDS)} default thresholds (placeholders - see config/thresholds.py).")
        else:
            print("Thresholds table already has data - not overwriting.")

        # Seed a default motor row
        motor = db.query(models.MotorInfo).filter_by(motor_id=settings.motor_id).first()
        if not motor:
            db.add(models.MotorInfo(
                motor_id=settings.motor_id,
                motor_type="3-phase AC induction motor",
                rated_voltage=230,
            ))
            db.commit()
            print(f"Seeded default motor_info row for {settings.motor_id}.")

        # Seed demo_mode setting
        setting = db.query(models.SystemSetting).filter_by(key="demo_mode").first()
        if not setting:
            db.add(models.SystemSetting(key="demo_mode", value="true" if settings.demo_mode_default else "false"))
            db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    run()
