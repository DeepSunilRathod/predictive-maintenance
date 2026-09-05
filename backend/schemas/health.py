from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel


class HealthOut(BaseModel):
    motor_id: str
    health_score: Optional[float]        # 0-100, None if insufficient data
    status: Literal["GOOD", "WARNING", "CRITICAL", "UNKNOWN"]
    risk_level: Literal["LOW", "MEDIUM", "HIGH", "UNKNOWN"]
    recommended_action: str
    last_fault_detected: Optional[str]
    last_fault_timestamp: Optional[datetime]
    operating_hours: float
    basis: str   # explains how the score was derived (rule-based vs ML)
