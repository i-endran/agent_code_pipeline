from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.models import AgentExecutionLog
from app.services.audit_service import audit_service
from pydantic import BaseModel

router = APIRouter()


class AgentStateResponse(BaseModel):
    """Response schema for agent execution state."""
    id: str
    task_id: str
    agent_name: str
    model: str
    provider: str
    temperature: float
    max_tokens: int
    started_at: str
    completed_at: str = None
    status: str
    commit_hash: str = None
    
    class Config:
        from_attributes = True


@router.get("/task/{task_id}", response_model=List[AgentStateResponse])
async def get_task_audit_log(task_id: str, db: Session = Depends(get_db)):
    """
    Returns all agent executions for a task.
    
    This provides a complete audit trail of which agents ran,
    with what configuration, for a specific task.
    """
    executions = audit_service.get_states_by_task(task_id, db)
    
    if not executions:
        raise HTTPException(
            status_code=404,
            detail=f"No agent executions found for task {task_id}"
        )
    
    return [
        AgentStateResponse(
            id=exec.id,
            task_id=exec.task_id,
            agent_name=exec.agent_name,
            model=exec.model,
            provider=exec.provider,
            temperature=exec.temperature,
            max_tokens=exec.max_tokens,
            started_at=exec.started_at.isoformat(),
            completed_at=exec.completed_at.isoformat() if exec.completed_at else None,
            status=exec.status,
            commit_hash=exec.commit_hash
        )
        for exec in executions
    ]


@router.get("/state/{state_id}")
async def get_agent_state(state_id: str, db: Session = Depends(get_db)):
    """
    Returns full agent configuration for a state ID.
    
    Includes all hyperparameters, guardrails, policies, and user prompts
    that were active when the agent executed.
    """
    execution = audit_service.get_state_by_id(state_id, db)
    
    if not execution:
        raise HTTPException(
            status_code=404,
            detail=f"Agent state {state_id} not found"
        )
    
    return {
        "id": execution.id,
        "task_id": execution.task_id,
        "agent_name": execution.agent_name,
        "configuration": {
            "model": execution.model,
            "provider": execution.provider,
            "temperature": execution.temperature,
            "max_tokens": execution.max_tokens,
            "guardrails": execution.guardrails,
            "policies": execution.policies,
            "enforcement_prompt": execution.enforcement_prompt,
            "tools": execution.tools,
            "user_prompt": execution.user_prompt
        },
        "execution": {
            "started_at": execution.started_at.isoformat(),
            "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
            "status": execution.status,
            "error_message": execution.error_message
        },
        "git": {
            "commit_hash": execution.commit_hash,
            "commit_message": execution.commit_message
        },
        "artifact_path": execution.config_artifact_path
    }


@router.get("/commit/{commit_hash}")
async def get_state_by_commit(commit_hash: str, db: Session = Depends(get_db)):
    """
    Finds agent state associated with a Git commit.
    
    Given a commit hash from your repository, this returns the complete
    agent configuration that generated that commit.
    """
    execution = audit_service.get_state_by_commit(commit_hash, db)
    
    if not execution:
        raise HTTPException(
            status_code=404,
            detail=f"No agent state found for commit {commit_hash}"
        )
    
    return {
        "state_id": execution.id,
        "agent_name": execution.agent_name,
        "task_id": execution.task_id,
        "model": execution.model,
        "temperature": execution.temperature,
        "commit_message": execution.commit_message,
        "full_config_url": f"/api/audit/state/{execution.id}"
    }
