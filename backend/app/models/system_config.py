"""
System Configuration Model

Key-value settings stored in DB for dynamic configuration.
"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime

from app.db.database import Base


class SystemConfig(Base):
    """Key-value configuration persisted in the database."""
    __tablename__ = "system_config"

    key = Column(String(100), primary_key=True)
    value = Column(String(500), nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
