"""
Webhook Model

Model for storing outbound webhook configurations.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, JSON, DateTime

from app.db.database import Base


class Webhook(Base):
    """Outbound webhook configuration."""
    __tablename__ = "webhooks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    url = Column(String(500), nullable=False)
    secret = Column(String(500), nullable=True)  # HMAC secret
    events = Column(JSON, nullable=False, default=list)  # ["task_completed", "agent_failed"]
    platform = Column(String(50), default="custom")  # custom, slack, teams
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
