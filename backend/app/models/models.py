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


class Repository(Base):
    __tablename__ = "repositories"
    id = Column(Integer, primary_key=True, index=True)
    source_url = Column(String, unique=True, index=True)
    local_path = Column(String)
    clone_status = Column(String, default="pending")  # pending, cloned, error
    last_synced = Column(DateTime, default=datetime.utcnow)
    
    tasks = relationship("Task", back_populates="repository")

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(String, primary_key=True, index=True)
    pipeline_id = Column(Integer, ForeignKey("pipelines.id"), nullable=False)
    
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    current_stage = Column(Enum(AgentStage), nullable=True)
    progress = Column(Integer, default=0)
    
    # JSON field for full configuration
    config = Column(JSON)
    
    # Consumption metrics
    token_usage = Column(JSON, nullable=False, default=dict)
    total_tokens = Column(Integer, default=0)
    total_cost = Column(Float, default=0.0)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    
    # Relationships
    repository_id = Column(Integer, ForeignKey("repositories.id"), nullable=True)
    repository = relationship("Repository", back_populates="tasks")
    artifacts = relationship("TaskArtifact", back_populates="task")
    pipeline = relationship("Pipeline", back_populates="tasks")
    stage_logs = relationship("StageLog", back_populates="task")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class TaskArtifact(Base):
    __tablename__ = "task_artifacts"
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String, ForeignKey("tasks.id"))
    artifact_type = Column(String)  # feature_doc, dpia, data_flow, plan, patch
    file_path = Column(String)      # Relative to storage/artifacts
    created_at = Column(DateTime, default=datetime.utcnow)
    
    task = relationship("Task", back_populates="artifacts")


class AgentExecutionLog(Base):
    """Agent execution audit log - captures full agent state for each run."""
    __tablename__ = "agent_execution_logs"
    
    id = Column(String, primary_key=True, index=True)  # UUID
    task_id = Column(String, ForeignKey("tasks.id"))
    agent_name = Column(String)  # scribe, architect, forge, sentinel, phoenix
    
    # Agent Configuration Snapshot
    model = Column(String)
    provider = Column(String)
    temperature = Column(Float)
    max_tokens = Column(Integer)
    guardrails = Column(JSON)
    policies = Column(JSON)
    enforcement_prompt = Column(Text)
    tools = Column(JSON)
    user_prompt = Column(Text, nullable=True)
    
    # Execution Metadata
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    status = Column(String, default="in_progress")  # in_progress, success, failed
    error_message = Column(Text, nullable=True)
    
    # Git Integration (for Forge commits)
    commit_hash = Column(String, nullable=True)
    commit_message = Column(Text, nullable=True)
    
    # Artifact reference
    config_artifact_path = Column(String, nullable=True)
    
    # Relationship
    task = relationship("Task", backref="agent_executions")


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


class Connector(Base):
    """External platform connector (GitHub, Slack, etc.)"""
    __tablename__ = "connectors"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)  # github, gitlab, slack, teams
    config = Column(JSON, nullable=False, default=dict)  # tokens, urls, etc.
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
