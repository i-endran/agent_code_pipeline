"""
Webhooks CRUD API

CRUD operations for managing outbound webhooks.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from app.db.database import get_db
from app.models.webhook import Webhook
from app.schemas.schemas import WebhookCreate, WebhookResponse

router = APIRouter()


@router.post("/", response_model=WebhookResponse, status_code=201)
async def create_webhook(webhook: WebhookCreate, db: Session = Depends(get_db)):
    """Create a new webhook."""
    db_webhook = Webhook(**webhook.model_dump())
    db.add(db_webhook)
    db.commit()
    db.refresh(db_webhook)
    return db_webhook


@router.get("/", response_model=List[WebhookResponse])
async def list_webhooks(db: Session = Depends(get_db)):
    """List all webhooks."""
    return db.query(Webhook).all()


@router.get("/{webhook_id}", response_model=WebhookResponse)
async def get_webhook(webhook_id: int, db: Session = Depends(get_db)):
    """Get a specific webhook."""
    webhook = db.query(Webhook).filter(Webhook.id == webhook_id).first()
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    return webhook


@router.put("/{webhook_id}", response_model=WebhookResponse)
async def update_webhook(webhook_id: int, webhook_in: WebhookCreate, db: Session = Depends(get_db)):
    """Update a webhook."""
    db_webhook = db.query(Webhook).filter(Webhook.id == webhook_id).first()
    if not db_webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    for key, value in webhook_in.model_dump().items():
        setattr(db_webhook, key, value)
    
    db.commit()
    db.refresh(db_webhook)
    return db_webhook


@router.delete("/{webhook_id}", status_code=204)
async def delete_webhook(webhook_id: int, db: Session = Depends(get_db)):
    """Delete a webhook."""
    db_webhook = db.query(Webhook).filter(Webhook.id == webhook_id).first()
    if not db_webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    db.delete(db_webhook)
    db.commit()
    return None
