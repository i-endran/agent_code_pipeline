"""
Approval API Routes

Endpoints for managing human-in-the-loop approval workflows.
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.approval import ApprovalRequest, ApprovalAction, ApprovalCheckpoint, ApprovalStatus
from app.schemas.schemas import (
    ApprovalRequestResponse,
    ApprovalActionCreate,
    ApprovalActionResponse,
    ApprovalDashboardResponse,
    ApprovalCheckpointEnum,
    ApprovalStatusEnum
)
from app.services.approval_service import approval_service

router = APIRouter()


@router.get("/pending", response_model=List[ApprovalRequestResponse])
async def list_pending_approvals(
    task_id: Optional[str] = Query(None),
    checkpoint: Optional[ApprovalCheckpointEnum] = Query(None),
    db: Session = Depends(get_db)
):
    """
    List all pending approval requests.
    
    - **task_id**: Optional filter by task ID
    - **checkpoint**: Optional filter by checkpoint type
    """
    checkpoint_model = ApprovalCheckpoint(checkpoint.value) if checkpoint else None
    approvals = approval_service.get_pending_approvals(db, task_id, checkpoint_model)
    return approvals


@router.get("/dashboard", response_model=ApprovalDashboardResponse)
async def get_approval_dashboard(
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get approval dashboard with stats and recent activity.
    
    Returns pending approvals and recent actions.
    """
    # Get counts by status
    pending_count = db.query(ApprovalRequest).filter(
        ApprovalRequest.status == ApprovalStatus.PENDING
    ).count()
    
    approved_count = db.query(ApprovalRequest).filter(
        ApprovalRequest.status == ApprovalStatus.APPROVED
    ).count()
    
    rejected_count = db.query(ApprovalRequest).filter(
        ApprovalRequest.status == ApprovalStatus.REJECTED
    ).count()
    
    timeout_count = db.query(ApprovalRequest).filter(
        ApprovalRequest.status == ApprovalStatus.TIMEOUT
    ).count()
    
    # Get pending requests
    pending_requests = db.query(ApprovalRequest).filter(
        ApprovalRequest.status == ApprovalStatus.PENDING
    ).order_by(ApprovalRequest.created_at.desc()).limit(limit).all()
    
    # Get recent actions
    recent_actions = db.query(ApprovalAction).order_by(
        ApprovalAction.created_at.desc()
    ).limit(limit).all()
    
    return {
        "pending_count": pending_count,
        "approved_count": approved_count,
        "rejected_count": rejected_count,
        "timeout_count": timeout_count,
        "pending_requests": pending_requests,
        "recent_actions": recent_actions
    }


@router.get("/{approval_id}", response_model=ApprovalRequestResponse)
async def get_approval_request(
    approval_id: int,
    db: Session = Depends(get_db)
):
    """Get specific approval request with artifacts and actions."""
    approval = db.query(ApprovalRequest).filter(ApprovalRequest.id == approval_id).first()
    if not approval:
        raise HTTPException(status_code=404, detail="Approval request not found")
    return approval


@router.post("/{approval_id}/approve", response_model=ApprovalActionResponse)
async def approve_request(
    approval_id: int,
    action_data: ApprovalActionCreate,
    db: Session = Depends(get_db)
):
    """
    Approve an approval request.
    
    Resumes the pipeline execution from the checkpoint.
    """
    try:
        action = approval_service.approve_request(
            db=db,
            approval_id=approval_id,
            user_name=action_data.user_name,
            comment=action_data.comment,
            feedback=action_data.feedback
        )
        return action
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{approval_id}/reject", response_model=ApprovalActionResponse)
async def reject_request(
    approval_id: int,
    action_data: ApprovalActionCreate,
    db: Session = Depends(get_db)
):
    """
    Reject an approval request.
    
    Routes back to the agent with feedback for rework.
    """
    if not action_data.comment:
        raise HTTPException(
            status_code=400,
            detail="Comment is required when rejecting"
        )
    
    try:
        action = approval_service.reject_request(
            db=db,
            approval_id=approval_id,
            user_name=action_data.user_name,
            comment=action_data.comment,
            feedback=action_data.feedback
        )
        return action
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/task/{task_id}", response_model=List[ApprovalRequestResponse])
async def get_task_approvals(
    task_id: str,
    db: Session = Depends(get_db)
):
    """Get all approval requests for a specific task."""
    approvals = db.query(ApprovalRequest).filter(
        ApprovalRequest.task_id == task_id
    ).order_by(ApprovalRequest.created_at.desc()).all()
    
    return approvals


@router.post("/check-timeouts")
async def check_approval_timeouts(db: Session = Depends(get_db)):
    """
    Check for timed-out approval requests and handle them.
    
    This endpoint can be called by a scheduled task or manually.
    """
    timed_out = approval_service.check_timeouts(db)
    
    return {
        "checked_at": datetime.utcnow(),
        "timed_out_count": len(timed_out),
        "timed_out_ids": [req.id for req in timed_out]
    }
