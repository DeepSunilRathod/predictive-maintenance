from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database.connection import get_db
from services.system_settings import get_demo_mode, set_demo_mode
from services.demo_generator import demo_generator

router = APIRouter(prefix="/api/settings", tags=["settings"])


class DemoModeIn(BaseModel):
    enabled: bool


@router.get("/demo-mode")
def read_demo_mode(db: Session = Depends(get_db)):
    return {"enabled": get_demo_mode(db)}


@router.post("/demo-mode")
def write_demo_mode(payload: DemoModeIn, db: Session = Depends(get_db)):
    set_demo_mode(db, payload.enabled)
    if payload.enabled:
        demo_generator.start()
    else:
        demo_generator.stop()
    return {"enabled": payload.enabled}
