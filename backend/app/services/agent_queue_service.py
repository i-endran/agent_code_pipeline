"""
Agent Queue Service

Manages per-agent priority queues: enqueue, dequeue, priority adjustment, aging.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.agent_queue import AgentQueueItem, QueueItemStatus
from app.models.models import AgentStage

logger = logging.getLogger(__name__)

# Aging: +1 priority for every AGING_INTERVAL_MINUTES an item has been waiting
AGING_INTERVAL_MINUTES = 30
MAX_PRIORITY = 10
MIN_PRIORITY = 1


class AgentQueueService:
    """Manages per-agent priority queues."""

    def enqueue(
        self,
        db: Session,
        task_id: str,
        agent_stage: AgentStage,
        context: Dict[str, Any],
        priority: int = 5,
        reason: str = "user_set"
    ) -> AgentQueueItem:
        """
        Add a task to an agent's queue.

        Args:
            db: Database session
            task_id: Task ID
            agent_stage: Target agent
            context: Pipeline context snapshot
            priority: Initial priority (1-10)
            reason: Why this priority was set
        """
        priority = max(MIN_PRIORITY, min(MAX_PRIORITY, priority))

        item = AgentQueueItem(
            task_id=task_id,
            agent_stage=agent_stage,
            priority=priority,
            priority_reason=reason,
            status=QueueItemStatus.QUEUED,
            context=context,
            retry_count=0
        )
        db.add(item)
        db.commit()
        db.refresh(item)

        logger.info(
            f"Enqueued task {task_id} to {agent_stage.value} queue "
            f"with priority {priority} ({reason})"
        )
        return item

    def dequeue(self, db: Session, agent_stage: AgentStage) -> Optional[AgentQueueItem]:
        """
        Pop the highest-priority queued item for an agent.
        Applies aging boost before selection.

        Returns None if the queue is empty.
        """
        # Apply aging first
        self._apply_aging_for_stage(db, agent_stage)

        item = (
            db.query(AgentQueueItem)
            .filter(
                AgentQueueItem.agent_stage == agent_stage,
                AgentQueueItem.status == QueueItemStatus.QUEUED
            )
            .order_by(
                AgentQueueItem.priority.desc(),   # Highest priority first
                AgentQueueItem.enqueued_at.asc()   # Oldest first at same priority
            )
            .first()
        )

        if item:
            item.status = QueueItemStatus.PROCESSING
            item.started_at = datetime.utcnow()
            db.commit()
            db.refresh(item)
            logger.info(
                f"Dequeued item {item.id} (task {item.task_id}) from "
                f"{agent_stage.value} queue, priority={item.priority}"
            )

        return item

    def boost_priority(
        self,
        db: Session,
        item_id: int,
        delta: int = 2,
        reason: str = "review_bump"
    ) -> AgentQueueItem:
        """Increment an item's priority by delta."""
        item = self._get_queued_item(db, item_id)
        old_priority = item.priority
        item.priority = min(MAX_PRIORITY, item.priority + delta)
        item.priority_reason = reason
        db.commit()
        db.refresh(item)

        logger.info(
            f"Boosted item {item_id} priority: {old_priority} → {item.priority} ({reason})"
        )
        return item

    def set_priority(
        self,
        db: Session,
        item_id: int,
        new_priority: int,
        reason: str = "user_set"
    ) -> AgentQueueItem:
        """Set an item's priority to an absolute value."""
        item = self._get_queued_item(db, item_id)
        old_priority = item.priority
        item.priority = max(MIN_PRIORITY, min(MAX_PRIORITY, new_priority))
        item.priority_reason = reason
        db.commit()
        db.refresh(item)

        logger.info(
            f"Set item {item_id} priority: {old_priority} → {item.priority} ({reason})"
        )
        return item

    def promote_to_next(self, db: Session, item_id: int) -> AgentQueueItem:
        """Set priority to MAX so the item is picked next."""
        return self.set_priority(db, item_id, MAX_PRIORITY, reason="promote")

    def get_queue(
        self,
        db: Session,
        agent_stage: AgentStage,
        include_processing: bool = False
    ) -> List[AgentQueueItem]:
        """Get all items in an agent's queue, ordered by effective priority."""
        statuses = [QueueItemStatus.QUEUED]
        if include_processing:
            statuses.append(QueueItemStatus.PROCESSING)

        return (
            db.query(AgentQueueItem)
            .filter(
                AgentQueueItem.agent_stage == agent_stage,
                AgentQueueItem.status.in_(statuses)
            )
            .order_by(
                AgentQueueItem.priority.desc(),
                AgentQueueItem.enqueued_at.asc()
            )
            .all()
        )

    def get_all_queues_summary(self, db: Session) -> Dict[str, Any]:
        """Get a summary of all agent queues (counts per stage)."""
        results = (
            db.query(
                AgentQueueItem.agent_stage,
                AgentQueueItem.status,
                func.count(AgentQueueItem.id)
            )
            .filter(AgentQueueItem.status.in_([
                QueueItemStatus.QUEUED, QueueItemStatus.PROCESSING
            ]))
            .group_by(AgentQueueItem.agent_stage, AgentQueueItem.status)
            .all()
        )

        summary = {}
        for stage in AgentStage:
            summary[stage.value] = {"queued": 0, "processing": 0}

        for stage, status, count in results:
            summary[stage.value][status.value] = count

        return summary

    def mark_done(self, db: Session, item_id: int) -> AgentQueueItem:
        """Mark a queue item as completed."""
        item = db.query(AgentQueueItem).filter(AgentQueueItem.id == item_id).first()
        if not item:
            raise ValueError(f"Queue item {item_id} not found")
        item.status = QueueItemStatus.DONE
        item.completed_at = datetime.utcnow()
        db.commit()
        db.refresh(item)
        return item

    def mark_failed(
        self, db: Session, item_id: int, error: str = None
    ) -> AgentQueueItem:
        """Mark a queue item as failed."""
        item = db.query(AgentQueueItem).filter(AgentQueueItem.id == item_id).first()
        if not item:
            raise ValueError(f"Queue item {item_id} not found")
        item.status = QueueItemStatus.FAILED
        item.completed_at = datetime.utcnow()
        item.error_message = error
        db.commit()
        db.refresh(item)
        return item

    def apply_aging(self, db: Session) -> int:
        """
        Bulk aging pass: +1 priority for every AGING_INTERVAL that has elapsed
        since enqueue, for all queued items. Returns number of items updated.
        """
        now = datetime.utcnow()
        threshold = now - timedelta(minutes=AGING_INTERVAL_MINUTES)

        items = (
            db.query(AgentQueueItem)
            .filter(
                AgentQueueItem.status == QueueItemStatus.QUEUED,
                AgentQueueItem.enqueued_at <= threshold,
                AgentQueueItem.priority < MAX_PRIORITY
            )
            .all()
        )

        updated = 0
        for item in items:
            elapsed = (now - item.enqueued_at).total_seconds() / 60
            intervals = int(elapsed // AGING_INTERVAL_MINUTES)
            # Target priority = base + intervals, but don't exceed MAX
            target = min(MAX_PRIORITY, MIN_PRIORITY + intervals)
            if target > item.priority:
                item.priority = target
                item.priority_reason = "aging"
                updated += 1

        if updated:
            db.commit()
            logger.info(f"Aging pass: updated {updated} queue items")

        return updated

    # --- Internal helpers ---

    def _get_queued_item(self, db: Session, item_id: int) -> AgentQueueItem:
        """Get a queued item or raise."""
        item = db.query(AgentQueueItem).filter(AgentQueueItem.id == item_id).first()
        if not item:
            raise ValueError(f"Queue item {item_id} not found")
        if item.status != QueueItemStatus.QUEUED:
            raise ValueError(
                f"Queue item {item_id} is not queued (status={item.status.value})"
            )
        return item

    def _apply_aging_for_stage(self, db: Session, agent_stage: AgentStage):
        """Apply aging only for a specific stage (called before dequeue)."""
        now = datetime.utcnow()
        threshold = now - timedelta(minutes=AGING_INTERVAL_MINUTES)

        items = (
            db.query(AgentQueueItem)
            .filter(
                AgentQueueItem.agent_stage == agent_stage,
                AgentQueueItem.status == QueueItemStatus.QUEUED,
                AgentQueueItem.enqueued_at <= threshold,
                AgentQueueItem.priority < MAX_PRIORITY
            )
            .all()
        )

        for item in items:
            elapsed = (now - item.enqueued_at).total_seconds() / 60
            intervals = int(elapsed // AGING_INTERVAL_MINUTES)
            target = min(MAX_PRIORITY, MIN_PRIORITY + intervals)
            if target > item.priority:
                item.priority = target
                item.priority_reason = "aging"

        if items:
            db.commit()


# Singleton
agent_queue_service = AgentQueueService()
