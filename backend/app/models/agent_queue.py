"""
Agent Queue Models

Per-agent priority queues for task scheduling.
Each agent has its own queue; items carry adjustable priority.
"""

import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, JSON, ForeignKey
from sqlalchemy.orm import relationship

from app.db.database import Base
from app.models.models import AgentStage


class QueueItemStatus(str, enum.Enum):
    """Status of an item in an agent queue."""
    QUEUED = "queued"
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed"


class AgentQueueItem(Base):
    """A task item sitting in an agent's queue, waiting to be processed."""
    __tablename__ = "agent_queue_items"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String, ForeignKey("tasks.id"), nullable=False, index=True)
    agent_stage = Column(Enum(AgentStage), nullable=False, index=True)

    # Priority: 1 (lowest) to 10 (highest). Higher = picked first.
    priority = Column(Integer, default=5, nullable=False, index=True)
    priority_reason = Column(String(255), default="user_set")  # user_set, review_bump, aging, promote

    # Status
    status = Column(Enum(QueueItemStatus), default=QueueItemStatus.QUEUED, index=True)

    # Pipeline context snapshot for the agent to consume
    context = Column(JSON, nullable=False, default=dict)

    # Retry tracking
    retry_count = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)

    # Timing
    enqueued_at = Column(DateTime, default=datetime.utcnow, index=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Relationship
    task = relationship("Task", backref="queue_items")
