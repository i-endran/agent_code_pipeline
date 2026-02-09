"""
Database Models for Pipeline and Tasks
"""

import enum
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, JSON, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.db.database import Base


class TaskStatus(str, enum.Enum):
    """Pipeline task status."""
    PENDING = "pending"
    PROCESSING = "processing"
    AWAITING_REVIEW = "awaiting_review"
    AWAITING_RELEASE = "awaiting_release"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentStage(str, enum.Enum):
    """Agent stage identifiers."""
    SCRIBE = "scribe"
    ARCHITECT = "architect"
    FORGE = "forge"
    HERALD = "herald"
    SENTINEL = "sentinel"
    PHOENIX = "phoenix"


class Pipeline(Base):
    """Pipeline configuration model."""
    __tablename__ = "pipelines"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Agent configurations (JSON)
    agent_configs = Column(JSON, nullable=False, default=dict)
    
    # Enabled agents (sequential)
    enabled_agents = Column(JSON, nullable=False, default=list)
    
    # Tasks relationship
    tasks = relationship("Task", back_populates="pipeline")


class Task(Base):
    """Pipeline task execution model."""
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    pipeline_id = Column(Integer, ForeignKey("pipelines.id"), nullable=False)
    
    # Status tracking
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    current_stage = Column(Enum(AgentStage), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Context and artifacts
    context = Column(JSON, nullable=False, default=dict)
    artifacts = Column(JSON, nullable=False, default=dict)
    
    # Token tracking
    token_usage = Column(JSON, nullable=False, default=dict)
    estimated_tokens = Column(Integer, default=0)
    actual_tokens = Column(Integer, default=0)
    estimated_cost = Column(Float, default=0.0)
    actual_cost = Column(Float, default=0.0)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    
    # Relationships
    pipeline = relationship("Pipeline", back_populates="tasks")
    stage_logs = relationship("StageLog", back_populates="task")


class StageLog(Base):
    """Log entry for each agent stage execution."""
    __tablename__ = "stage_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    
    stage = Column(Enum(AgentStage), nullable=False)
    status = Column(String(50), nullable=False)  # started, completed, failed
    
    # Timing
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Float, nullable=True)
    
    # Tokens
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    
    # Input/Output
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Relationship
    task = relationship("Task", back_populates="stage_logs")
