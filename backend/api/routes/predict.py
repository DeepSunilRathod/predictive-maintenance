from fastapi import APIRouter
from schemas.predict import PredictIn, PredictOut
from ml.predict import predict as ml_predict

router = APIRouter(prefix="/api/predict", tags=["predict"])


@router.post("", response_model=PredictOut)
def run_prediction(payload: PredictIn):
    result = ml_predict(payload.model_dump())
    return PredictOut(**result)
