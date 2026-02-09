"""
Tasks API Routes

Task creation, status tracking, and management.
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.models import Task, Pipeline, TaskStatus, StageLog
from app.schemas.schemas import (
    TaskCreate,
    TaskResponse,
    TaskDetailResponse,
    TaskStatusEnum
)
from app.services.agent_config import calculate_token_estimate

router = APIRouter()


@router.post("/", response_model=TaskResponse, status_code=201)
async def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db)
):
    """
    Create and submit a new pipeline task for execution.
    
    The task will be queued for processing by Celery workers.
    """
    # Validate pipeline exists
    pipeline = db.query(Pipeline).filter(Pipeline.id == task.pipeline_id).first()
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    
    if not pipeline.enabled_agents:
        raise HTTPException(
            status_code=400,
            detail="Pipeline has no enabled agents"
        )
    
    # Calculate token estimates
    estimates = calculate_token_estimate(pipeline.enabled_agents)
    
    # Create task
    db_task = Task(
        pipeline_id=task.pipeline_id,
        status=TaskStatus.PENDING,
        context=pipeline.agent_configs,
        estimated_tokens=estimates["total_tokens"],
        estimated_cost=estimates["total_cost"]
    )
    
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    # TODO: Dispatch to Celery queue
    # from app.celery_app import run_pipeline
    # run_pipeline.delay(db_task.id)
    
    return db_task


@router.get("/", response_model=List[TaskResponse])
async def list_tasks(
    status: Optional[TaskStatusEnum] = None,
    pipeline_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all tasks with optional filtering.
    
    - **status**: Filter by task status
    - **pipeline_id**: Filter by pipeline
    """
    query = db.query(Task)
    
    if status:
        query = query.filter(Task.status == status)
    if pipeline_id:
        query = query.filter(Task.pipeline_id == pipeline_id)
    
    tasks = query.order_by(Task.created_at.desc()).offset(skip).limit(limit).all()
    return tasks


@router.get("/running", response_model=List[TaskResponse])
async def list_running_tasks(db: Session = Depends(get_db)):
    """Get all currently running tasks."""
    running_statuses = [
        TaskStatus.PENDING,
        TaskStatus.PROCESSING,
        TaskStatus.AWAITING_REVIEW,
        TaskStatus.AWAITING_RELEASE
    ]
    
    tasks = db.query(Task).filter(
        Task.status.in_(running_statuses)
    ).order_by(Task.created_at.desc()).all()
    
    return tasks


@router.get("/{task_id}", response_model=TaskDetailResponse)
async def get_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    """Get detailed task information including artifacts and token usage."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.get("/{task_id}/logs")
async def get_task_logs(
    task_id: int,
    db: Session = Depends(get_db)
):
    """Get execution logs for each agent stage."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    logs = db.query(StageLog).filter(
        StageLog.task_id == task_id
    ).order_by(StageLog.started_at).all()
    
    return {
        "task_id": task_id,
        "logs": [
            {
                "stage": log.stage.value,
                "status": log.status,
                "started_at": log.started_at,
                "completed_at": log.completed_at,
                "duration_seconds": log.duration_seconds,
                "input_tokens": log.input_tokens,
                "output_tokens": log.output_tokens,
                "error_message": log.error_message
            }
            for log in logs
        ]
    }


@router.post("/{task_id}/cancel", response_model=TaskResponse)
async def cancel_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    """Cancel a running task."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel task with status: {task.status.value}"
        )
    
    task.status = TaskStatus.CANCELLED
    task.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(task)
    
    # TODO: Revoke Celery task
    
    return task


@router.get("/dashboard/tokens")
async def get_token_dashboard(
    days: int = Query(default=7, ge=1, le=90),
    db: Session = Depends(get_db)
):
    """
    Get token consumption dashboard data.
    
    Returns aggregated token usage over the specified period.
    """
    from datetime import timedelta
    
    cutoff = datetime.utcnow() - timedelta(days=days)
    
    tasks = db.query(Task).filter(
        Task.created_at >= cutoff,
        Task.status == TaskStatus.COMPLETED
    ).all()
    
    total_tokens = sum(t.actual_tokens for t in tasks)
    total_cost = sum(t.actual_cost for t in tasks)
    
    # Aggregate by day
    daily_usage = {}
    for task in tasks:
        day = task.created_at.strftime("%Y-%m-%d")
        if day not in daily_usage:
            daily_usage[day] = {"tokens": 0, "cost": 0.0, "tasks": 0}
        daily_usage[day]["tokens"] += task.actual_tokens
        daily_usage[day]["cost"] += task.actual_cost
        daily_usage[day]["tasks"] += 1
    
    return {
        "period_days": days,
        "total_tokens": total_tokens,
        "total_cost": round(total_cost, 4),
        "total_tasks": len(tasks),
        "daily_usage": daily_usage
    }
