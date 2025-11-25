from fastapi import WebSocket
from typing import Dict

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, order_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[order_id] = websocket

    def disconnect(self, order_id: str):
        self.active_connections.pop(order_id, None)

    async def send_json(self, order_id: str, data):
        ws = self.active_connections.get(order_id)
        if ws:
            await ws.send_json(data)
