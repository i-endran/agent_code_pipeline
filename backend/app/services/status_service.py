import logging
from typing import Dict, Optional, Any
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class StatusService:
    """
    Manages in-memory status for agents and tasks.
    Tracks what each agent is doing and what's next in their queue.
    """
    
    def __init__(self):
        # agent_id -> { status, current_task: { name, progress, started_at }, next_task: { name, queued_at } }
        self.agent_statuses: Dict[str, Dict[str, Any]] = {
            "scribe": {"status": "idle", "current": None, "next": None},
            "architect": {"status": "idle", "current": None, "next": None},
            "forge": {"status": "idle", "current": None, "next": None},
            "sentinel": {"status": "idle", "current": None, "next": None},
            "phoenix": {"status": "idle", "current": None, "next": None}
        }
        self.task_progress: Dict[str, Dict[str, Any]] = {}

    def update_agent_status(
        self, 
        agent_id: str, 
        status: str, 
        current_task_name: Optional[str] = None, 
        progress: Optional[int] = None,
        next_task_name: Optional[str] = None
    ):
        """Update the status of a specific agent."""
        if agent_id not in self.agent_statuses:
            return

        self.agent_statuses[agent_id]["status"] = status
        
        if status == "running" and current_task_name:
            self.agent_statuses[agent_id]["current"] = {
                "name": current_task_name,
                "progress": progress if progress is not None else 0,
                "started_at": datetime.utcnow().isoformat()
            }
        elif status == "idle":
            self.agent_statuses[agent_id]["current"] = None
            
        if next_task_name is not None:
            self.agent_statuses[agent_id]["next"] = {
                "name": next_task_name,
                "queued_at": datetime.utcnow().isoformat()
            } if next_task_name else None

        # In a real app, we would broadcast here via a callback or event bus
        logger.info(f"Agent {agent_id} status updated to {status}")

    def get_all_statuses(self) -> Dict[str, Any]:
        """Get the current status of all agents."""
        return self.agent_statuses

status_service = StatusService()
