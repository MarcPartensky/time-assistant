from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.websocket_manager import WebSocketManager

router = APIRouter()
manager = WebSocketManager()


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Client #{client_id} dit: {data}")
    except WebSocketDisconnect:
        manager.disconnect(client_id)
        await manager.broadcast(f"Client #{client_id} s'est déconnecté.")
