import logging
import asyncio
from typing import Dict, Any, Optional
from app.api.websocket import manager
from app.services.status_service import status_service

logger = logging.getLogger(__name__)

def send_task_update(task_id: str, data: Dict[str, Any]):
    """
    Synchronous wrapper to send task updates from Celery workers.
    Also updates the status_service for agent activity tracking.
    """
    # Extract agent status info if present
    current_stage = data.get("current_stage")
    status = data.get("status", "running")
    message = data.get("message", "")
    progress = data.get("progress")

    if current_stage:
        # Update agent status in status_service
        status_service.update_agent_status(
            agent_id=current_stage,
            status="running" if status != "completed" else "idle",
            current_task_name=message if status == "running" else None,
            progress=progress
        )

    # WebSocket broadcast message
    update_msg = {
        "type": "status_update",
        "task_id": task_id,
        "status": status,
        "message": message,
        **{k: v for k, v in data.items() if k not in ["status", "message"]}
    }

    # Since Celery runs in a separate process, we usually use a bridge.
    # For now, we'll try to use the manager directly if we're in the same process,
    # or just log it. In a real distributed setup, this would publish to Redis/RabbitMQ.
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.ensure_future(manager.broadcast_to_task(0, update_msg))
            # Also send to specific task if id is not 0
            if task_id != "0":
                try:
                    tid = int(task_id)
                    asyncio.ensure_future(manager.broadcast_to_task(tid, update_msg))
                except ValueError:
                    pass
        else:
            asyncio.run(manager.broadcast_to_task(0, update_msg))
    except Exception as e:
        logger.debug(f"Could not send WS update: {e}")
    
    logger.info(f"Task {task_id} update: {message}")
