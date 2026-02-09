"""
Pipelines API Routes

CRUD operations for pipeline configurations.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.models import Pipeline, TaskStatus
from app.schemas.schemas import (
    PipelineCreate, 
    PipelineResponse, 
    PipelineAgentConfigs,
    TokenEstimate
)
from app.services.agent_config import get_agent_configs, calculate_token_estimate

router = APIRouter()


@router.post("/", response_model=PipelineResponse, status_code=201)
async def create_pipeline(
    pipeline: PipelineCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new pipeline configuration.
    
    The pipeline defines which agents are enabled and their configurations.
    Agents must be enabled sequentially (cannot skip agents in between).
    """
    # Validate sequential agent enablement
    agent_configs = pipeline.agent_configs.model_dump()
    enabled_agents = []
    
    agent_order = ["scribe", "architect", "forge", "herald", "sentinel", "phoenix"]
    found_disabled = False
    
    for agent in agent_order:
        if agent_configs[agent]["enabled"]:
            if found_disabled:
                raise HTTPException(
                    status_code=400,
                    detail=f"Cannot enable {agent}: agents must be enabled sequentially without gaps"
                )
            enabled_agents.append(agent)
        else:
            found_disabled = True
    
    if not enabled_agents:
        raise HTTPException(
            status_code=400,
            detail="At least one agent must be enabled"
        )
    
    # Create pipeline
    db_pipeline = Pipeline(
        name=pipeline.name,
        description=pipeline.description,
        agent_configs=agent_configs,
        enabled_agents=enabled_agents
    )
    
    db.add(db_pipeline)
    db.commit()
    db.refresh(db_pipeline)
    
    return db_pipeline


@router.get("/", response_model=List[PipelineResponse])
async def list_pipelines(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all pipeline configurations."""
    pipelines = db.query(Pipeline).offset(skip).limit(limit).all()
    return pipelines


@router.get("/{pipeline_id}", response_model=PipelineResponse)
async def get_pipeline(
    pipeline_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific pipeline by ID."""
    pipeline = db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    return pipeline


@router.get("/{pipeline_id}/estimate")
async def estimate_tokens(
    pipeline_id: int,
    db: Session = Depends(get_db)
):
    """
    Get token and cost estimation for a pipeline.
    
    Returns estimated tokens and costs for each enabled agent.
    """
    pipeline = db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    
    estimates = calculate_token_estimate(pipeline.enabled_agents)
    
    return {
        "pipeline_id": pipeline_id,
        "pipeline_name": pipeline.name,
        "estimates": estimates["agents"],
        "total_tokens": estimates["total_tokens"],
        "total_cost": estimates["total_cost"]
    }


@router.delete("/{pipeline_id}", status_code=204)
async def delete_pipeline(
    pipeline_id: int,
    db: Session = Depends(get_db)
):
    """Delete a pipeline configuration."""
    pipeline = db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    
    db.delete(pipeline)
    db.commit()
    return None
