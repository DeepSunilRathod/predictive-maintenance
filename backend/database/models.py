"""
SQLAlchemy ORM models. Mirrors database/schema.sql exactly - if you change
one, change the other.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.sql import func

from database.connection import Base


class SensorData(Base):
    __tablename__ = "sensor_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    motor_id = Column(String(64), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    temperature = Column(Float, nullable=True)
    current = Column(Float, nullable=True)
    vibration = Column(Float, nullable=True)
    rpm = Column(Float, nullable=True)
    source = Column(String(16), nullable=False, default="real")  # 'real' | 'demo'


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    motor_id = Column(String(64), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    parameter = Column(String(32), nullable=False)
    value = Column(Float, nullable=False)
    threshold = Column(Float, nullable=False)
    severity = Column(String(16), nullable=False)  # INFO | WARNING | CRITICAL
    message = Column(String(255), nullable=False)
    possible_cause = Column(String(255), nullable=True)
    recommended_action = Column(String(255), nullable=True)
    status = Column(String(16), nullable=False, default="ACTIVE")  # ACTIVE | ACKNOWLEDGED | RESOLVED


class Threshold(Base):
    __tablename__ = "thresholds"

    id = Column(Integer, primary_key=True, autoincrement=True)
    parameter = Column(String(32), nullable=False, unique=True)
    unit = Column(String(32), nullable=False, default="")
    normal_max = Column(Float, nullable=True)
    warning_max = Column(Float, nullable=True)
    critical_max = Column(Float, nullable=True)
    extra_json = Column(Text, nullable=True)  # for RPM band-style config etc.
    source_note = Column(String(255), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class MotorInfo(Base):
    __tablename__ = "motor_info"

    id = Column(Integer, primary_key=True, autoincrement=True)
    motor_id = Column(String(64), nullable=False, unique=True)
    motor_type = Column(String(64), nullable=True)
    rated_voltage = Column(Float, nullable=True)
    rated_power_kw = Column(Float, nullable=True)
    rated_rpm = Column(Float, nullable=True)
    installation_date = Column(DateTime(timezone=True), nullable=True)
    total_operating_hours = Column(Float, nullable=False, default=0.0)


class SystemSetting(Base):
    """Runtime-toggleable settings, e.g. demo mode on/off."""
    __tablename__ = "system_settings"

    key = Column(String(64), primary_key=True)
    value = Column(String(255), nullable=False)
