from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field


class SensorReadingIn(BaseModel):
    """Payload posted by the microcontroller (or the demo generator)."""
    motor_id: str = Field(default="MOTOR-001")
    temperature: Optional[float] = Field(default=None, description="Degrees Celsius")
    current: Optional[float] = Field(default=None, description="Amps")
    vibration: Optional[float] = Field(default=None, description="mm/s RMS")
    rpm: Optional[float] = Field(default=None, description="Revolutions per minute")
    source: Literal["real", "demo"] = "real"
    timestamp: Optional[datetime] = None


class SensorReadingOut(BaseModel):
    id: int
    motor_id: str
    timestamp: datetime
    temperature: Optional[float]
    current: Optional[float]
    vibration: Optional[float]
    rpm: Optional[float]
    source: str

    class Config:
        from_attributes = True


class ParameterSummary(BaseModel):
    parameter: str
    unit: str
    value: Optional[float]
    status: Literal["NORMAL", "WARNING", "CRITICAL", "NO_DATA"]
    trend: Literal["up", "down", "flat", "unknown"]
    min_value: Optional[float]
    max_value: Optional[float]
    last_updated: Optional[datetime]
    connected: bool


class LatestSensorsResponse(BaseModel):
    motor_id: str
    demo_mode: bool
    parameters: list[ParameterSummary]
