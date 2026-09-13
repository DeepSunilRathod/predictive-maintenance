from fastapi import APIRouter
from schemas.predict import PredictOut
from ml.keras_predict import predict_from_window
from services.reading_buffer import reading_buffer
from config.settings import settings
from datetime import datetime, timezone

router = APIRouter(prefix="/api/predict", tags=["predict"])


@router.post("", response_model=PredictOut)
def run_prediction():
    window = reading_buffer.get_window(settings.motor_id)
    if window is None:
        fill = reading_buffer.fill_ratio(settings.motor_id)
        return PredictOut(
            model_available=False,
            status="NOT_ENOUGH_DATA",
            failure_probability=None,
            predicted_condition=None,
            confidence=None,
            remaining_useful_life_hours=None,
            note=f"Buffering sensor readings for prediction ({fill*100:.0f}% of required window collected).",
            prediction_timestamp=datetime.now(timezone.utc),
        )

    result = predict_from_window(window)
    return PredictOut(**result)