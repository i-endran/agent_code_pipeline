"""
WebSocket Routes

Real-time status updates for task execution.
"""

from typing import Dict
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
import json

router = APIRouter()

# Active WebSocket connections per task
active_connections: Dict[int, list] = {}


class ConnectionManager:
    """Manages WebSocket connections for real-time updates."""
    
    def __init__(self):
        self.active_connections: Dict[int, list[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, task_id: int):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        if task_id not in self.active_connections:
            self.active_connections[task_id] = []
        self.active_connections[task_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, task_id: int):
        """Remove a WebSocket connection."""
        if task_id in self.active_connections:
            if websocket in self.active_connections[task_id]:
                self.active_connections[task_id].remove(websocket)
            if not self.active_connections[task_id]:
                del self.active_connections[task_id]
    
    async def broadcast_to_task(self, task_id: int, message: dict):
        """Send a message to all connections for a task."""
        if task_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[task_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    disconnected.append(connection)
            
            for conn in disconnected:
                self.disconnect(conn, task_id)
    
    async def broadcast_all(self, message: dict):
        """Send a message to all connected clients."""
        for task_id in list(self.active_connections.keys()):
            await self.broadcast_to_task(task_id, message)


manager = ConnectionManager()


@router.websocket("/ws/status/{task_id}")
async def task_status_websocket(websocket: WebSocket, task_id: int):
    """
    WebSocket endpoint for real-time task status updates.
    
    Connect to receive updates for a specific task.
    Messages include status changes, progress, and stage completions.
    """
    await manager.connect(websocket, task_id)
    
    try:
        # Send initial connection confirmation
        await websocket.send_json({
            "type": "connected",
            "task_id": task_id,
            "message": f"Connected to task {task_id} status stream"
        })
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Wait for messages (ping/pong or commands)
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=30.0  # 30 second timeout
                )
                
                # Handle ping
                if data == "ping":
                    await websocket.send_json({"type": "pong"})
                
            except asyncio.TimeoutError:
                # Send keepalive
                try:
                    await websocket.send_json({"type": "keepalive"})
                except Exception:
                    break
                    
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket, task_id)


@router.websocket("/ws/all")
async def all_tasks_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for all task updates.
    
    Connect to receive updates for all running tasks.
    """
    await websocket.accept()
    
    # Use task_id 0 for global subscriptions
    if 0 not in manager.active_connections:
        manager.active_connections[0] = []
    manager.active_connections[0].append(websocket)
    
    try:
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to global status stream"
        })
        
        while True:
            try:
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=30.0
                )
                
                if data == "ping":
                    await websocket.send_json({"type": "pong"})
                    
            except asyncio.TimeoutError:
                try:
                    await websocket.send_json({"type": "keepalive"})
                except Exception:
                    break
                    
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket, 0)


# Helper function for Celery workers to send updates
async def send_task_update(task_id: int, status: str, stage: str, progress: int, message: str):
    """
    Send a task update to all connected WebSocket clients.
    
    Called by Celery workers during task execution.
    """
    update = {
        "type": "status_update",
        "task_id": task_id,
        "status": status,
        "current_stage": stage,
        "progress_percent": progress,
        "message": message
    }
    
    await manager.broadcast_to_task(task_id, update)
    await manager.broadcast_to_task(0, update)  # Also send to global subscribers
