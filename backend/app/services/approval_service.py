"""
Approval Service for Human-in-the-Loop Workflows

Manages approval requests, actions, and orchestration.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.models.approval import ApprovalRequest, ApprovalAction, ApprovalCheckpoint, ApprovalStatus, STAGE_PRIORITY
from app.models.models import Task, TaskStatus
from app.utils.task_utils import send_task_update

logger = logging.getLogger(__name__)


class ApprovalService:
    """Service for managing approval workflows."""
    
    def create_approval_request(
        self,
        db: Session,
        task_id: str,
        checkpoint: ApprovalCheckpoint,
        agent_name: str,
        artifact_paths: List[str],
        summary: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        timeout_minutes: int = 60,
        auto_approve_on_timeout: bool = False
    ) -> ApprovalRequest:
        """
        Create a new approval request and pause the pipeline.
        
        Args:
            db: Database session
            task_id: Task ID
            checkpoint: Approval checkpoint type
            agent_name: Name of the agent requesting approval
            artifact_paths: List of artifact file paths for review
            summary: Brief summary for quick review
            details: Additional context (diff stats, test results, etc.)
            timeout_minutes: Minutes until timeout
            auto_approve_on_timeout: Whether to auto-approve on timeout
            
        Returns:
            Created ApprovalRequest
        """
        # Calculate timeout
        timeout_at = datetime.utcnow() + timedelta(minutes=timeout_minutes)
        
        # Create approval request with auto-assigned priority
        priority = STAGE_PRIORITY.get(checkpoint, 5)
        
        approval_request = ApprovalRequest(
            task_id=task_id,
            checkpoint=checkpoint,
            agent_name=agent_name,
            status=ApprovalStatus.PENDING,
            artifact_paths=artifact_paths,
            summary=summary,
            details=details,
            timeout_at=timeout_at,
            auto_approve_on_timeout=auto_approve_on_timeout,
            priority=priority
        )
        
        db.add(approval_request)
        db.commit()
        db.refresh(approval_request)
        
        # Update task status
        task = db.query(Task).filter(Task.id == task_id).first()
        if task:
            task.status = TaskStatus.AWAITING_REVIEW
            db.commit()
        
        # Send WebSocket notification
        send_task_update(task_id, {
            "status": "awaiting_review",
            "message": f"Waiting for approval at {checkpoint.value}",
            "approval_id": approval_request.id,
            "checkpoint": checkpoint.value
        })
        
        logger.info(f"Created approval request {approval_request.id} for task {task_id} at checkpoint {checkpoint.value}")
        
        return approval_request
    
    def approve_request(
        self,
        db: Session,
        approval_id: int,
        user_name: str = "System",
        comment: Optional[str] = None,
        feedback: Optional[Dict[str, Any]] = None
    ) -> ApprovalAction:
        """
        Approve an approval request and resume the pipeline.
        
        Args:
            db: Database session
            approval_id: Approval request ID
            user_name: Name of the user approving
            comment: Optional approval comment
            feedback: Optional structured feedback
            
        Returns:
            Created ApprovalAction
        """
        approval_request = db.query(ApprovalRequest).filter(ApprovalRequest.id == approval_id).first()
        if not approval_request:
            raise ValueError(f"Approval request {approval_id} not found")
        
        if approval_request.status != ApprovalStatus.PENDING:
            raise ValueError(f"Approval request {approval_id} is already {approval_request.status.value}")
        
        # Create approval action
        action = ApprovalAction(
            approval_request_id=approval_id,
            action=ApprovalStatus.APPROVED,
            user_name=user_name,
            comment=comment,
            feedback=feedback
        )
        
        db.add(action)
        
        # Update approval request
        approval_request.status = ApprovalStatus.APPROVED
        approval_request.resolved_at = datetime.utcnow()
        
        db.commit()
        db.refresh(action)
        
        # Resume pipeline
        self._resume_pipeline(db, approval_request.task_id, approval_request.checkpoint)
        
        logger.info(f"Approved request {approval_id} by {user_name}")
        
        return action
    
    def reject_request(
        self,
        db: Session,
        approval_id: int,
        user_name: str = "System",
        comment: Optional[str] = None,
        feedback: Optional[Dict[str, Any]] = None
    ) -> ApprovalAction:
        """
        Reject an approval request and route back to the agent.
        
        Args:
            db: Database session
            approval_id: Approval request ID
            user_name: Name of the user rejecting
            comment: Required rejection comment
            feedback: Optional structured feedback for the agent
            
        Returns:
            Created ApprovalAction
        """
        approval_request = db.query(ApprovalRequest).filter(ApprovalRequest.id == approval_id).first()
        if not approval_request:
            raise ValueError(f"Approval request {approval_id} not found")
        
        if approval_request.status != ApprovalStatus.PENDING:
            raise ValueError(f"Approval request {approval_id} is already {approval_request.status.value}")
        
        # Create rejection action
        action = ApprovalAction(
            approval_request_id=approval_id,
            action=ApprovalStatus.REJECTED,
            user_name=user_name,
            comment=comment or "Rejected without comment",
            feedback=feedback
        )
        
        db.add(action)
        
        # Update approval request
        approval_request.status = ApprovalStatus.REJECTED
        approval_request.resolved_at = datetime.utcnow()
        
        db.commit()
        db.refresh(action)
        
        # Route back to agent with feedback
        self._handle_rejection(db, approval_request.task_id, approval_request.checkpoint, feedback)
        
        logger.info(f"Rejected request {approval_id} by {user_name}: {comment}")
        
        return action
    
    def check_timeouts(self, db: Session) -> List[ApprovalRequest]:
        """
        Check for timed-out approval requests and handle them.
        
        Args:
            db: Database session
            
        Returns:
            List of timed-out approval requests
        """
        now = datetime.utcnow()
        
        # Find pending requests that have timed out
        timed_out = db.query(ApprovalRequest).filter(
            ApprovalRequest.status == ApprovalStatus.PENDING,
            ApprovalRequest.timeout_at <= now
        ).all()
        
        for approval_request in timed_out:
            if approval_request.auto_approve_on_timeout:
                # Auto-approve
                action = ApprovalAction(
                    approval_request_id=approval_request.id,
                    action=ApprovalStatus.TIMEOUT,
                    user_name="System (Auto-Approved)",
                    comment="Automatically approved due to timeout"
                )
                db.add(action)
                
                approval_request.status = ApprovalStatus.APPROVED
                approval_request.resolved_at = now
                
                # Resume pipeline
                self._resume_pipeline(db, approval_request.task_id, approval_request.checkpoint)
                
                logger.info(f"Auto-approved request {approval_request.id} due to timeout")
            else:
                # Auto-reject
                action = ApprovalAction(
                    approval_request_id=approval_request.id,
                    action=ApprovalStatus.TIMEOUT,
                    user_name="System (Auto-Rejected)",
                    comment="Automatically rejected due to timeout"
                )
                db.add(action)
                
                approval_request.status = ApprovalStatus.TIMEOUT
                approval_request.resolved_at = now
                
                # Mark task as failed
                task = db.query(Task).filter(Task.id == approval_request.task_id).first()
                if task:
                    task.status = TaskStatus.FAILED
                    task.error_message = f"Approval timeout at {approval_request.checkpoint.value}"
                
                logger.warning(f"Auto-rejected request {approval_request.id} due to timeout")
        
        db.commit()
        
        return timed_out
    
    def get_pending_approvals(
        self,
        db: Session,
        task_id: Optional[str] = None,
        checkpoint: Optional[ApprovalCheckpoint] = None
    ) -> List[ApprovalRequest]:
        """
        Get pending approval requests.
        
        Args:
            db: Database session
            task_id: Optional task ID filter
            checkpoint: Optional checkpoint filter
            
        Returns:
            List of pending approval requests
        """
        query = db.query(ApprovalRequest).filter(ApprovalRequest.status == ApprovalStatus.PENDING)
        
        if task_id:
            query = query.filter(ApprovalRequest.task_id == task_id)
        if checkpoint:
            query = query.filter(ApprovalRequest.checkpoint == checkpoint)
        
        return query.order_by(
            ApprovalRequest.priority.desc(),  # Highest priority first
            ApprovalRequest.created_at.asc()   # Oldest first within same priority
        ).all()
    
    def _resume_pipeline(self, db: Session, task_id: str, checkpoint: ApprovalCheckpoint):
        """Resume pipeline execution after approval."""
        from app.tasks.tasks import resume_pipeline
        
        # Update task status
        task = db.query(Task).filter(Task.id == task_id).first()
        if task:
            task.status = TaskStatus.PROCESSING
            db.commit()
        
        # Send WebSocket notification
        send_task_update(task_id, {
            "status": "processing",
            "message": f"Approval granted. Resuming from {checkpoint.value}...",
            "checkpoint": checkpoint.value
        })
        
        # Trigger Celery task to resume
        resume_pipeline.delay(task_id, checkpoint.value)
        
        logger.info(f"Resuming pipeline for task {task_id} from checkpoint {checkpoint.value}")
    
    def _handle_rejection(
        self,
        db: Session,
        task_id: str,
        checkpoint: ApprovalCheckpoint,
        feedback: Optional[Dict[str, Any]]
    ):
        """Handle rejection by routing back to the agent."""
        # Update task status
        task = db.query(Task).filter(Task.id == task_id).first()
        if task:
            task.status = TaskStatus.PROCESSING
            
            # Store feedback in task config for agent to use
            if feedback and task.config:
                agent_key = checkpoint.value.split('_')[0]  # e.g., "scribe" from "scribe_output"
                if agent_key in task.config:
                    task.config[agent_key]["rejection_feedback"] = feedback
            
            db.commit()
        
        # Send WebSocket notification
        send_task_update(task_id, {
            "status": "processing",
            "message": f"Approval rejected. Re-running {checkpoint.value}...",
            "checkpoint": checkpoint.value,
            "feedback": feedback
        })
        
        # Trigger Celery task to re-run the agent
        from app.tasks.tasks import rerun_agent
        rerun_agent.delay(task_id, checkpoint.value, feedback)
        
        logger.info(f"Re-running agent for task {task_id} at checkpoint {checkpoint.value}")


# Singleton instance
approval_service = ApprovalService()
