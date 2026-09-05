"""
Tracks active WebSocket connections and broadcasts live sensor updates
to every connected dashboard client.
"""
from typing import List
from fastapi import WebSocket
import json
import logging

logger = logging.getLogger("connection_manager")


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total clients: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total clients: {len(self.active_connections)}")

    async def broadcast(self, payload: dict):
        dead = []
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(payload, default=str))
            except Exception:
                dead.append(connection)
        for d in dead:
            self.disconnect(d)


manager = ConnectionManager()
