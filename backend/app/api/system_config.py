"""
System Configuration API

Endpoints for reading and updating dynamic system settings.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict

from app.db.database import get_db
from app.services.config_service import config_service

router = APIRouter()


class ConfigUpdateRequest(BaseModel):
    value: str


class ConfigResponse(BaseModel):
    key: str
    value: str


@router.get("", response_model=Dict[str, str])
async def get_all_config(db: Session = Depends(get_db)):
    """Get all system configuration values."""
    return config_service.get_all(db)


@router.get("/{key}", response_model=ConfigResponse)
async def get_config(key: str, db: Session = Depends(get_db)):
    """Get a specific configuration value."""
    value = config_service.get(db, key)
    if value is None:
        raise HTTPException(status_code=404, detail=f"Config key '{key}' not found")
    return {"key": key, "value": value}


@router.patch("/{key}", response_model=ConfigResponse)
async def update_config(key: str, body: ConfigUpdateRequest, db: Session = Depends(get_db)):
    """Update a configuration value."""
    row = config_service.set(db, key, body.value)
    return {"key": row.key, "value": row.value}
