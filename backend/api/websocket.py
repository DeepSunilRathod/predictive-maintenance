from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services.connection_manager import manager

router = APIRouter()


@router.websocket("/ws/live")
async def websocket_live(websocket: WebSocket):
    """
    Real-time push channel. On connect, clients receive a hello message;
    afterwards they receive a `sensor_update` message every time a new
    reading is persisted (from either the demo generator or POST /api/sensors/data).
    """
    await manager.connect(websocket)
    try:
        await websocket.send_json({"type": "hello", "message": "connected"})
        while True:
            # We don't expect client -> server messages, but read (and ignore)
            # to detect disconnects promptly.
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
