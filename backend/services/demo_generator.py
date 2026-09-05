"""
DEMO / SIMULATION data generator.

Generates synthetic sensor readings so the dashboard can be exercised before
hardware is connected. Every row it writes is tagged source='demo' in the
database and the API always reports demo_mode=true alongside it, so demo
data can never be mistaken for real measurements downstream.

This is a background asyncio task started from main.py's startup event,
and stopped automatically as soon as real hardware data starts arriving
(or when demo mode is switched off via /api/settings/demo-mode).
"""
import asyncio
import math
import random
import time
import logging
from datetime import datetime, timezone
from services.threshold_service import get_thresholds, evaluate_status, build_alert_if_needed, has_recent_active_alert

from database.connection import SessionLocal
from database import models
from services.threshold_service import get_thresholds, evaluate_status, build_alert_if_needed
from services.connection_manager import manager
from services.health_service import compute_health_score
from config.settings import settings

logger = logging.getLogger("demo_generator")

SCENARIOS = [
    "normal",
    "temp_rise",
    "current_rise",
    "vibration_rise",
    "rpm_drop",
    "multi_fault",
]


class DemoGenerator:
    def __init__(self):
        self.running = False
        self._task = None
        self._t0 = time.time()
        self._scenario = "normal"
        self._scenario_switch_at = time.time() + random.uniform(40, 90)

    def is_running(self) -> bool:
        return self.running

    def start(self):
        if not self.running:
            self.running = True
            self._task = asyncio.create_task(self._loop())
            logger.info("Demo generator started.")

    def stop(self):
        self.running = False
        if self._task:
            self._task.cancel()
        logger.info("Demo generator stopped.")

    def _maybe_rotate_scenario(self):
        if time.time() >= self._scenario_switch_at:
            self._scenario = random.choice(SCENARIOS)
            self._scenario_switch_at = time.time() + random.uniform(45, 100)
            logger.info(f"Demo scenario -> {self._scenario}")

    def _generate_reading(self) -> dict:
        self._maybe_rotate_scenario()
        elapsed = time.time() - self._t0

        # Baselines with gentle natural noise/oscillation
        temp = 42 + 3 * math.sin(elapsed / 30) + random.uniform(-0.8, 0.8)
        current = 2.6 + 0.3 * math.sin(elapsed / 20) + random.uniform(-0.15, 0.15)
        vibration = 1.3 + 0.2 * math.sin(elapsed / 15) + random.uniform(-0.1, 0.1)
        rpm = 1440 + 8 * math.sin(elapsed / 25) + random.uniform(-3, 3)

        s = self._scenario
        if s == "temp_rise":
            temp += min(45, (elapsed % 120) * 0.5)
        elif s == "current_rise":
            current += min(3.0, (elapsed % 120) * 0.03)
        elif s == "vibration_rise":
            vibration += min(6.0, (elapsed % 120) * 0.06)
        elif s == "rpm_drop":
            rpm -= min(300, (elapsed % 120) * 3)
        elif s == "multi_fault":
            temp += min(30, (elapsed % 120) * 0.3)
            current += min(1.8, (elapsed % 120) * 0.02)
            vibration += min(3.5, (elapsed % 120) * 0.03)

        return {
            "temperature": round(temp, 2),
            "current": round(current, 2),
            "vibration": round(vibration, 2),
            "rpm": round(rpm, 1),
        }

    async def _loop(self):
        try:
            while self.running:
                reading = self._generate_reading()
                await self._persist_and_broadcast(reading)
                await asyncio.sleep(2)
        except asyncio.CancelledError:
            pass

    async def _persist_and_broadcast(self, reading: dict):
        db = SessionLocal()
        try:
            row = models.SensorData(
                motor_id=settings.motor_id,
                temperature=reading["temperature"],
                current=reading["current"],
                vibration=reading["vibration"],
                rpm=reading["rpm"],
                source="demo",
            )
            db.add(row)
            db.commit()
            db.refresh(row)

            thresholds = get_thresholds(db)
            new_alerts = []
            for param in ("temperature", "current", "vibration", "rpm"):
                value = reading[param]
                status = evaluate_status(param, value, thresholds)
                alert_data = build_alert_if_needed(param, value, status, thresholds)
                if alert_data and not has_recent_active_alert(db, settings.motor_id, param, status):
                    alert = models.Alert(motor_id=settings.motor_id, **alert_data)
                    db.add(alert)
                    db.commit()
                    db.refresh(alert)
                    new_alerts.append({
                        "id": alert.id,
                        "parameter": alert.parameter,
                        "severity": alert.severity,
                        "message": alert.message,
                        "timestamp": alert.timestamp.isoformat() if alert.timestamp else None,
                    })

            score, health_status, _ = compute_health_score(reading, thresholds)

            await manager.broadcast({
                "type": "sensor_update",
                "demo_mode": True,
                "motor_id": settings.motor_id,
                "timestamp": row.timestamp.isoformat() if row.timestamp else datetime.now(timezone.utc).isoformat(),
                "data": reading,
                "health_score": score,
                "health_status": health_status,
                "new_alerts": new_alerts,
            })
        except Exception as e:
            logger.exception(f"Demo generator persist/broadcast failed: {e}")
        finally:
            db.close()


demo_generator = DemoGenerator()
