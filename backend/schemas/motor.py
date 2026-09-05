from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class MotorInfoOut(BaseModel):
    motor_id: str
    motor_type: Optional[str]
    rated_voltage: Optional[float]
    rated_power_kw: Optional[float]
    rated_rpm: Optional[float]
    installation_date: Optional[datetime]
    total_operating_hours: float

    class Config:
        from_attributes = True


class MotorStatusOut(BaseModel):
    motor_id: str
    connection_status: str          # CONNECTED | DISCONNECTED | DEMO
    demo_mode: bool
    last_updated: Optional[datetime]
    system_status: str              # OK | DEGRADED | OFFLINE
