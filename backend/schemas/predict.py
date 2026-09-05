from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class PredictIn(BaseModel):
    temperature: float
    current: float
    vibration: float
    rpm: float


class PredictOut(BaseModel):
    model_available: bool
    status: str                          # e.g. WARNING, or "MODEL_NOT_AVAILABLE"
    failure_probability: Optional[float] = Field(default=None, ge=0, le=1)
    predicted_condition: Optional[str] = None
    confidence: Optional[float] = Field(default=None, ge=0, le=1)
    remaining_useful_life_hours: Optional[float] = None
    note: str
    prediction_timestamp: datetime
