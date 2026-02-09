"""
Agent Connector Mapping Model

Many-to-many mapping between Agents and Connectors/Webhooks.
Allows assigning specific tools to specific agents.
"""

from sqlalchemy import Column, Integer, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship

from app.db.database import Base
from app.models.models import AgentStage


class AgentConnectorMapping(Base):
    """Mapping between an Agent Stage and a Connector or Webhook."""
    __tablename__ = "agent_connector_mappings"

    id = Column(Integer, primary_key=True, index=True)
    agent_stage = Column(Enum(AgentStage), nullable=False, index=True)
    
    # Polymorphic-ish association (one or the other)
    connector_id = Column(Integer, ForeignKey("connectors.id"), nullable=True)
    webhook_id = Column(Integer, ForeignKey("webhooks.id"), nullable=True)
    
    is_active = Column(Boolean, default=True)
    
    # Relationships
    connector = relationship("Connector")
    webhook = relationship("Webhook") 
