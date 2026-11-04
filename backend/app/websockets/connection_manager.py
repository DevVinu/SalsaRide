import json
import logging
from typing import Dict, List, Set
from fastapi import WebSocket

logger = logging.getLogger("smartflow.websockets")


class ConnectionManager:
    def __init__(self):
        # junction_id -> set of active WebSockets
        self.junction_subscribers: Dict[str, Set[WebSocket]] = {}
        # Global admin subscribers
        self.admin_subscribers: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket, junction_id: Optional[str] = None):
        await websocket.accept()
        if junction_id:
            if junction_id not in self.junction_subscribers:
                self.junction_subscribers[junction_id] = set()
            self.junction_subscribers[junction_id].add(websocket)
            logger.info(f"WebSocket client connected to junction {junction_id}")
        else:
            self.admin_subscribers.add(websocket)
            logger.info("WebSocket admin client connected")

    def disconnect(self, websocket: WebSocket, junction_id: Optional[str] = None):
        if junction_id and junction_id in self.junction_subscribers:
            self.junction_subscribers[junction_id].discard(websocket)
            if not self.junction_subscribers[junction_id]:
                del self.junction_subscribers[junction_id]
        self.admin_subscribers.discard(websocket)
        logger.info("WebSocket client disconnected")

    async def broadcast_junction_update(self, junction_id: str, data: dict):
        """Broadcasts virtual signal & corridor traffic update to all connected subscribers."""
        payload = json.dumps(data, default=str)
        dead_sockets = []

        # Send to junction subscribers
        targets = list(self.junction_subscribers.get(junction_id, set()))
        for ws in targets:
            try:
                await ws.send_text(payload)
            except Exception:
                dead_sockets.append((ws, junction_id))

        # Send to admin dashboard
        for ws in list(self.admin_subscribers):
            try:
                await ws.send_text(payload)
            except Exception:
                dead_sockets.append((ws, None))

        for ws, j_id in dead_sockets:
            self.disconnect(ws, j_id)


from typing import Optional
ws_manager = ConnectionManager()

