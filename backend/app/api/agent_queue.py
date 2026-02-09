"""
Agent Queue API

Endpoints for viewing and managing per-agent priority queues.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict
from datetime import datetime

from app.db.database import get_db
from app.models.models import AgentStage
from app.models.agent_queue import AgentQueueItem, QueueItemStatus
from app.services.agent_queue_service import agent_queue_service

router = APIRouter()


# ── Schemas ──────────────────────────────────────────────

class QueueItemResponse(BaseModel):
    id: int
    task_id: str
    agent_stage: str
    priority: int
    priority_reason: str
    status: str
    retry_count: int
    enqueued_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    error_message: Optional[str]

    class Config:
        from_attributes = True


class SetPriorityRequest(BaseModel):
    priority: int = Field(ge=1, le=10, description="New priority (1-10)")
    reason: str = Field(default="user_set", description="Reason for change")


class BoostPriorityRequest(BaseModel):
    delta: int = Field(default=2, ge=1, le=5, description="Amount to boost")
    reason: str = Field(default="manual_boost", description="Reason for boost")


class QueueSummaryResponse(BaseModel):
    queues: Dict[str, Dict[str, int]]


# ── Endpoints ────────────────────────────────────────────

@router.get("", response_model=QueueSummaryResponse)
async def get_all_queues(db: Session = Depends(get_db)):
    """Get a summary of all agent queues (counts per stage)."""
    summary = agent_queue_service.get_all_queues_summary(db)
    return {"queues": summary}


@router.get("/{agent_stage}", response_model=List[QueueItemResponse])
async def get_agent_queue(
    agent_stage: str,
    include_processing: bool = False,
    db: Session = Depends(get_db)
):
    """Get all items in a specific agent's queue, ordered by priority."""
    try:
        stage = AgentStage(agent_stage)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid agent stage: {agent_stage}. "
                   f"Valid: {[s.value for s in AgentStage]}"
        )

    items = agent_queue_service.get_queue(db, stage, include_processing)
    return items


@router.patch("/items/{item_id}/priority", response_model=QueueItemResponse)
async def set_item_priority(
    item_id: int,
    body: SetPriorityRequest,
    db: Session = Depends(get_db)
):
    """Set an item's priority to an absolute value."""
    try:
        item = agent_queue_service.set_priority(
            db, item_id, body.priority, body.reason
        )
        return item
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/items/{item_id}/promote", response_model=QueueItemResponse)
async def promote_item(item_id: int, db: Session = Depends(get_db)):
    """Promote an item to max priority so it's picked next."""
    try:
        item = agent_queue_service.promote_to_next(db, item_id)
        return item
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/items/{item_id}/boost", response_model=QueueItemResponse)
async def boost_item(
    item_id: int,
    body: BoostPriorityRequest,
    db: Session = Depends(get_db)
):
    """Increment an item's priority by a delta."""
    try:
        item = agent_queue_service.boost_priority(
            db, item_id, body.delta, body.reason
        )
        return item
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/apply-aging")
async def apply_aging(db: Session = Depends(get_db)):
    """Trigger a manual aging pass across all queues."""
    updated = agent_queue_service.apply_aging(db)
    return {"updated_count": updated, "message": f"Aged {updated} queue items"}
