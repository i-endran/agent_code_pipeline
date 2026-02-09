from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.models import Connector
from app.schemas.schemas import ConnectorCreate, ConnectorResponse

router = APIRouter()

@router.post("/", response_model=ConnectorResponse, status_code=201)
async def create_connector(
    connector: ConnectorCreate,
    db: Session = Depends(get_db)
):
    """Create a new external platform connector."""
    db_connector = Connector(
        name=connector.name,
        type=connector.type,
        config=connector.config,
        is_active=connector.is_active
    )
    db.add(db_connector)
    db.commit()
    db.refresh(db_connector)
    return db_connector

@router.get("/", response_model=List[ConnectorResponse])
async def list_connectors(db: Session = Depends(get_db)):
    """List all configured connectors."""
    return db.query(Connector).all()

@router.get("/{connector_id}", response_model=ConnectorResponse)
async def get_connector(connector_id: int, db: Session = Depends(get_db)):
    """Get a specific connector by ID."""
    connector = db.query(Connector).filter(Connector.id == connector_id).first()
    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found")
    return connector

@router.put("/{connector_id}", response_model=ConnectorResponse)
async def update_connector(
    connector_id: int,
    connector_in: ConnectorCreate,
    db: Session = Depends(get_db)
):
    """Update a connector configuration."""
    db_connector = db.query(Connector).filter(Connector.id == connector_id).first()
    if not db_connector:
        raise HTTPException(status_code=404, detail="Connector not found")
    
    for field, value in connector_in.model_dump().items():
        setattr(db_connector, field, value)
    
    db.commit()
    db.refresh(db_connector)
    return db_connector

@router.delete("/{connector_id}", status_code=204)
async def delete_connector(connector_id: int, db: Session = Depends(get_db)):
    """Delete a connector."""
    connector = db.query(Connector).filter(Connector.id == connector_id).first()
    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found")
    
    db.delete(connector)
    db.commit()
    return None
