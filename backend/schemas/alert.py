from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel


class AlertOut(BaseModel):
    id: int
    motor_id: str
    timestamp: datetime
    parameter: str
    value: float
    threshold: float
    severity: Literal["INFO", "WARNING", "CRITICAL"]
    message: str
    possible_cause: Optional[str]
    recommended_action: Optional[str]
    status: Literal["ACTIVE", "ACKNOWLEDGED", "RESOLVED"]

    class Config:
        from_attributes = True
