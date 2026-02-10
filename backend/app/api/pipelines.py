"""
Pipelines API Routes

CRUD operations for pipeline configurations.
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid
from datetime import datetime
import os

from app.db.database import get_db
from app.models.models import Pipeline, TaskStatus, Task, Repository
from app.schemas.schemas import (
    PipelineCreate, 
    PipelineResponse, 
    PipelineAgentConfigs,
    TokenEstimate,
    PipelineRunRequest,
    ScribeInput, ArchitectInput, ForgeInput, SentinelInput, PhoenixInput
)
from app.services.agent_config import get_agent_configs, calculate_token_estimate
from app.services.repo_service import repo_service

router = APIRouter()

@router.post("/run", response_model=Dict[str, Any], status_code=201)
async def run_pipeline(
    request: PipelineRunRequest,
    db: Session = Depends(get_db)
):
    """
    Create a pipeline and immediately run it as a task.
    Handles repo cloning and context extraction.
    """
    # 1. Handle Repo
    repo = db.query(Repository).filter(Repository.source_url == request.repo_url).first()
    if not repo:
        repo = Repository(source_url=request.repo_url, clone_status="pending")
        db.add(repo)
        db.commit()
        db.refresh(repo)

    # Clone Repo
    repo_path = None
    try:
        # We need to use repo.id (int)
        repo_path = repo_service.clone_repo(repo.id, request.repo_url)
        repo.local_path = repo_path
        repo.clone_status = "cloned"
        db.commit()
    except Exception as e:
        print(f"Failed to clone repo: {e}")
        # Proceed even if clone fails, but context will be empty

    project_context = ""
    if repo_path:
        readme_path = os.path.join(repo_path, "README.md")
        if os.path.exists(readme_path):
            try:
                with open(readme_path, "r", encoding="utf-8") as f:
                    project_context = f.read()
            except Exception as e:
                print(f"Failed to read README.md: {e}")

    # 2. Construct Pipeline Config
    scribe_cfg = request.scribe_config

    agent_configs = {
        "scribe": ScribeInput(
            enabled=request.agents.get("scribe", {}).get("enabled", False),
            requirement_text=request.requirements,
            project_context=project_context,
            user_prompt=scribe_cfg.user_prompt if scribe_cfg else None,
            output_format=scribe_cfg.output_format if scribe_cfg else "markdown",
            selected_documents=scribe_cfg.selected_documents if scribe_cfg else ["feature_doc"]
        ).model_dump(),

        "architect": ArchitectInput(
            enabled=request.agents.get("architect", {}).get("enabled", False)
        ).model_dump(),

        "forge": ForgeInput(
            enabled=request.agents.get("forge", {}).get("enabled", False),
            repo_path=repo_path if repo_path else "",
            target_branch=request.branch
        ).model_dump(),

        "sentinel": SentinelInput(
            enabled=request.agents.get("sentinel", {}).get("enabled", False),
            target_branch=request.branch
        ).model_dump(),

        "phoenix": PhoenixInput(
            enabled=request.agents.get("phoenix", {}).get("enabled", False),
            release_branch="main"
        ).model_dump(),
    }

    enabled_agents = []
    # Order matters: scribe -> architect -> forge -> sentinel -> phoenix
    agent_order = ["scribe", "architect", "forge", "sentinel", "phoenix"]
    for agent in agent_order:
        # Check if enabled in input request or derived config
        if agent_configs[agent]["enabled"]:
             enabled_agents.append(agent)

    if not enabled_agents:
        raise HTTPException(status_code=400, detail="At least one agent must be enabled")

    # Create Pipeline
    pipeline = Pipeline(
        name=f"Run {request.branch} - {datetime.utcnow().isoformat()}",
        description=request.requirements[:100],
        agent_configs=agent_configs,
        enabled_agents=enabled_agents
    )
    db.add(pipeline)
    db.commit()
    db.refresh(pipeline)

    # 3. Create Task
    estimates = calculate_token_estimate(pipeline.enabled_agents)

    task_id = str(uuid.uuid4())
    task = Task(
        id=task_id,
        pipeline_id=pipeline.id,
        status=TaskStatus.PENDING,
        config=pipeline.agent_configs,
        # estimated_tokens/cost fields missing in model, skipping
        repository_id=repo.id if repo else None
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    # Trigger Celery Task (TODO: Uncomment when Celery is ready)
    # from app.celery_app import run_pipeline
    # run_pipeline.delay(task.id)

    return {"task_id": task.id}


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
    
    agent_order = ["scribe", "architect", "forge", "sentinel", "phoenix"]
    found_disabled = False
    
    for agent in agent_order:
        if agent in agent_configs and agent_configs[agent]["enabled"]:
            if found_disabled:
                raise HTTPException(
                    status_code=400,
                    detail=f"Cannot enable {agent}: agents must be enabled sequentially without gaps"
                )
            enabled_agents.append(agent)
        elif agent in agent_configs:
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
