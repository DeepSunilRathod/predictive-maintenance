"""
Predictive Maintenance System - FastAPI backend entrypoint.

Run with:
    cd backend
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import settings
from database.connection import SessionLocal
from database import init_db
from services.demo_generator import demo_generator
from services.system_settings import get_demo_mode

from api.routes import sensors, alerts, health, predict, motor, settings as settings_route
from api import websocket as websocket_route

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Initializing database (create tables if missing, seed defaults)...")
    try:
        init_db.run()
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        logger.error("Check backend/.env DB_* values and that MySQL is running - see docs/DATABASE_SETUP.md")
        raise

    db = SessionLocal()
    try:
        if get_demo_mode(db):
            demo_generator.start()
    finally:
        db.close()

    yield

    # Shutdown
    demo_generator.stop()


app = FastAPI(
    title="Predictive Maintenance API",
    description="IoT-based predictive maintenance system for a 230V AC induction motor.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sensors.router)
app.include_router(alerts.router)
app.include_router(health.router)
app.include_router(predict.router)
app.include_router(motor.router)
app.include_router(settings_route.router)
app.include_router(websocket_route.router)


@app.get("/")
def root():
    return {"service": "predictive-maintenance-api", "status": "running", "docs": "/docs"}


@app.get("/api/ping")
def ping():
    return {"status": "ok"}
