"""
Agent Mapping API

Manage assignments of connectors and webhooks to specific agents.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.database import get_db
from app.models.models import AgentStage, Connector
from app.models.webhook import Webhook
from app.models.agent_connector_mapping import AgentConnectorMapping
from app.schemas.schemas import ConnectorResponse, WebhookResponse, AgentConnectorMappingResponse

router = APIRouter()


class AssignConnectorRequest(BaseModel):
    connector_id: int


class AssignWebhookRequest(BaseModel):
    webhook_id: int


# --- Connectors ---

@router.get("/{agent_stage}/connectors", response_model=List[ConnectorResponse])
async def get_agent_connectors(agent_stage: str, db: Session = Depends(get_db)):
    """Get all connectors assigned to an agent."""
    try:
        stage = AgentStage(agent_stage)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid agent stage")
        
    mappings = db.query(AgentConnectorMapping).filter(
        AgentConnectorMapping.agent_stage == stage,
        AgentConnectorMapping.connector_id.isnot(None),
        AgentConnectorMapping.is_active == True
    ).all()
    
    return [m.connector for m in mappings if m.connector]


@router.post("/{agent_stage}/connectors", response_model=AgentConnectorMappingResponse)
async def assign_connector(
    agent_stage: str, 
    body: AssignConnectorRequest, 
    db: Session = Depends(get_db)
):
    """Assign a connector to an agent."""
    try:
        stage = AgentStage(agent_stage)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid agent stage")
        
    # Check if connector exists
    connector = db.query(Connector).filter(Connector.id == body.connector_id).first()
    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found")
        
    # Check existing mapping
    existing = db.query(AgentConnectorMapping).filter(
        AgentConnectorMapping.agent_stage == stage,
        AgentConnectorMapping.connector_id == body.connector_id
    ).first()
    
    if existing:
        existing.is_active = True
        db.commit()
        db.refresh(existing)
        return existing
        
    mapping = AgentConnectorMapping(
        agent_stage=stage,
        connector_id=body.connector_id
    )
    db.add(mapping)
    db.commit()
    db.refresh(mapping)
    return mapping


@router.delete("/{agent_stage}/connectors/{connector_id}", status_code=204)
async def remove_connector(
    agent_stage: str, 
    connector_id: int, 
    db: Session = Depends(get_db)
):
    """Remove a connector assignment from an agent."""
    try:
        stage = AgentStage(agent_stage)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid agent stage")
        
    mapping = db.query(AgentConnectorMapping).filter(
        AgentConnectorMapping.agent_stage == stage,
        AgentConnectorMapping.connector_id == connector_id
    ).first()
    
    if mapping:
        db.delete(mapping)
        db.commit()
    return None


# --- Webhooks ---

@router.get("/{agent_stage}/webhooks", response_model=List[WebhookResponse])
async def get_agent_webhooks(agent_stage: str, db: Session = Depends(get_db)):
    """Get all webhooks assigned to an agent."""
    try:
        stage = AgentStage(agent_stage)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid agent stage")
        
    mappings = db.query(AgentConnectorMapping).filter(
        AgentConnectorMapping.agent_stage == stage,
        AgentConnectorMapping.webhook_id.isnot(None),
        AgentConnectorMapping.is_active == True
    ).all()
    
    return [m.webhook for m in mappings if m.webhook]


@router.post("/{agent_stage}/webhooks", response_model=AgentConnectorMappingResponse)
async def assign_webhook(
    agent_stage: str, 
    body: AssignWebhookRequest, 
    db: Session = Depends(get_db)
):
    """Assign a webhook to an agent."""
    try:
        stage = AgentStage(agent_stage)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid agent stage")
        
    webhook = db.query(Webhook).filter(Webhook.id == body.webhook_id).first()
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
        
    existing = db.query(AgentConnectorMapping).filter(
        AgentConnectorMapping.agent_stage == stage,
        AgentConnectorMapping.webhook_id == body.webhook_id
    ).first()
    
    if existing:
        existing.is_active = True
        db.commit()
        db.refresh(existing)
        return existing
        
    mapping = AgentConnectorMapping(
        agent_stage=stage,
        webhook_id=body.webhook_id
    )
    db.add(mapping)
    db.commit()
    db.refresh(mapping)
    return mapping


@router.delete("/{agent_stage}/webhooks/{webhook_id}", status_code=204)
async def remove_webhook(
    agent_stage: str, 
    webhook_id: int, 
    db: Session = Depends(get_db)
):
    """Remove a webhook assignment from an agent."""
    try:
        stage = AgentStage(agent_stage)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid agent stage")
        
    mapping = db.query(AgentConnectorMapping).filter(
        AgentConnectorMapping.agent_stage == stage,
        AgentConnectorMapping.webhook_id == webhook_id
    ).first()
    
    if mapping:
        db.delete(mapping)
        db.commit()
    return None
