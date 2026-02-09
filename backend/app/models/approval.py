"""
Approval Models for Human-in-the-Loop Workflows

Tracks approval requests, actions, and history for pipeline checkpoints.
"""

import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, JSON, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.db.database import Base


class ApprovalCheckpoint(str, enum.Enum):
    """Approval checkpoint identifiers."""
    SCRIBE_OUTPUT = "scribe_output"
    ARCHITECT_PLAN = "architect_plan"
    FORGE_CODE = "forge_code"
    SENTINEL_REVIEW = "sentinel_review"
    PHOENIX_RELEASE = "phoenix_release"


class ApprovalStatus(str, enum.Enum):
    """Approval request status."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    TIMEOUT = "timeout"


class ApprovalRequest(Base):
    """Tracks approval requests at pipeline checkpoints."""
    __tablename__ = "approval_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String, ForeignKey("tasks.id"), nullable=False, index=True)
    
    # Checkpoint information
    checkpoint = Column(Enum(ApprovalCheckpoint), nullable=False)
    agent_name = Column(String(50), nullable=False)  # scribe, architect, forge, etc.
    
    # Status
    status = Column(Enum(ApprovalStatus), default=ApprovalStatus.PENDING, index=True)
    
    # Artifacts for review
    artifact_paths = Column(JSON, nullable=False, default=list)  # List of file paths
    summary = Column(Text, nullable=True)  # Brief summary for quick review
    details = Column(JSON, nullable=True)  # Additional context (diff stats, test results, etc.)
    
    # Timing
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    timeout_at = Column(DateTime, nullable=True)  # When to auto-approve/reject
    resolved_at = Column(DateTime, nullable=True)
    
    # Auto-approval settings
    auto_approve_on_timeout = Column(Boolean, default=False)
    
    # Relationships
    task = relationship("Task", backref="approval_requests")
    actions = relationship("ApprovalAction", back_populates="approval_request", cascade="all, delete-orphan")


class ApprovalAction(Base):
    """Logs approval/rejection actions with user feedback."""
    __tablename__ = "approval_actions"
    
    id = Column(Integer, primary_key=True, index=True)
    approval_request_id = Column(Integer, ForeignKey("approval_requests.id"), nullable=False)
    
    # Action details
    action = Column(Enum(ApprovalStatus), nullable=False)  # approved, rejected, timeout
    user_id = Column(String(100), nullable=True)  # Future: user authentication
    user_name = Column(String(255), nullable=True, default="System")
    
    # Feedback
    comment = Column(Text, nullable=True)  # User comments
    feedback = Column(JSON, nullable=True)  # Structured feedback for agent
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    # Relationship
    approval_request = relationship("ApprovalRequest", back_populates="actions")


class NotificationPreference(Base):
    """User notification preferences for approval requests."""
    __tablename__ = "notification_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=False, unique=True, index=True)
    
    # Notification channels
    email_enabled = Column(Boolean, default=True)
    email_address = Column(String(255), nullable=True)
    
    slack_enabled = Column(Boolean, default=False)
    slack_webhook_url = Column(String(500), nullable=True)
    
    teams_enabled = Column(Boolean, default=False)
    teams_webhook_url = Column(String(500), nullable=True)
    
    # Notification settings
    notify_on_request = Column(Boolean, default=True)
    notify_on_timeout_warning = Column(Boolean, default=True)
    timeout_warning_minutes = Column(Integer, default=15)  # Warn X minutes before timeout
    
    # Preferences per checkpoint
    checkpoint_preferences = Column(JSON, nullable=True)  # {"scribe_output": {"notify": true}, ...}
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
