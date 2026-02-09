"""
Pydantic Schemas for API Request/Response
"""

from datetime import datetime
from typing import Optional, Dict, List, Any
from pydantic import BaseModel, Field
from enum import Enum


class TaskStatusEnum(str, Enum):
    """Task status enum for API."""
    PENDING = "pending"
    PROCESSING = "processing"
    AWAITING_REVIEW = "awaiting_review"
    AWAITING_RELEASE = "awaiting_release"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentStageEnum(str, Enum):
    """Agent stage enum for API."""
    SCRIBE = "scribe"
    ARCHITECT = "architect"
    FORGE = "forge"
    SENTINEL = "sentinel"
    PHOENIX = "phoenix"


# ============ Agent Configuration Schemas ============

class AgentInputBase(BaseModel):
    """Base schema for agent inputs."""
    enabled: bool = False
    user_prompt: Optional[str] = None


class ScribeInput(AgentInputBase):
    """Input configuration for SCRIBE agent."""
    requirement_text: str = ""
    project_context: str = ""
    output_format: str = "markdown"  # markdown, docx, both
    selected_documents: List[str] = ["feature_doc"]


class ArchitectInput(AgentInputBase):
    """Input configuration for ARCHITECT agent."""
    tech_stack: List[str] = []
    architecture_notes: str = ""
    granularity: int = Field(default=3, ge=1, le=5)


class ForgeInput(AgentInputBase):
    """Input configuration for FORGE agent."""
    repo_path: str = ""
    target_branch: str = ""
    test_command: str = "npm test"
    lint_command: str = "npm run lint"


class HeraldInput(AgentInputBase):
    """Input configuration for HERALD agent."""
    git_provider: str = "github"  # github, gitlab, custom
    repo_url: str = ""
    mr_title_template: str = "[AUTO] {feature_name}"
    reviewer_webhook_url: str = ""
    labels: List[str] = []


class SentinelInput(AgentInputBase):
    """Input configuration for SENTINEL agent."""
    review_criteria: str = ""
    auto_approve_threshold: int = Field(default=85, ge=0, le=100)
    max_fix_iterations: int = Field(default=3, ge=1, le=10)
    target_branch: str = "develop"


class PhoenixInput(AgentInputBase):
    """Input configuration for PHOENIX agent."""
    release_branch: str = "main"
    chat_webhook_url: str = ""
    chat_platform: str = "slack"  # slack, teams, zoho, custom
    changelog_enabled: bool = True
    notification_template: str = ""
    merge_strategy: str = "squash"  # merge, squash, rebase


# ============ Pipeline Schemas ============

class PipelineAgentConfigs(BaseModel):
    """All agent configurations for a pipeline."""
    scribe: ScribeInput = ScribeInput()
    architect: ArchitectInput = ArchitectInput()
    forge: ForgeInput = ForgeInput()
    sentinel: SentinelInput = SentinelInput()
    phoenix: PhoenixInput = PhoenixInput()


class PipelineCreate(BaseModel):
    """Schema for creating a new pipeline."""
    name: str
    description: Optional[str] = None
    agent_configs: PipelineAgentConfigs


class PipelineResponse(BaseModel):
    """Schema for pipeline response."""
    id: int
    name: str
    description: Optional[str]
    created_at: datetime
    enabled_agents: List[str]
    agent_configs: Dict[str, Any]
    
    class Config:
        from_attributes = True


# ============ Task Schemas ============

class TaskCreate(BaseModel):
    """Schema for creating a new task."""
    pipeline_id: int


class TokenEstimate(BaseModel):
    """Token estimation for a pipeline."""
    agent: str
    estimated_tokens: int
    estimated_cost: float


class TaskResponse(BaseModel):
    """Schema for task response."""
    id: int
    pipeline_id: int
    status: TaskStatusEnum
    current_stage: Optional[AgentStageEnum]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    estimated_tokens: int
    actual_tokens: int
    estimated_cost: float
    actual_cost: float
    error_message: Optional[str]
    
    class Config:
        from_attributes = True


class TaskDetailResponse(TaskResponse):
    """Detailed task response with artifacts."""
    context: Dict[str, Any]
    artifacts: Dict[str, Any]
    token_usage: Dict[str, Any]


class TaskStatusUpdate(BaseModel):
    """WebSocket status update payload."""
    task_id: int
    status: TaskStatusEnum
    current_stage: Optional[AgentStageEnum]
    progress_percent: int
    message: str
    timestamp: datetime


# ============ Agent Config Response ============

class AgentConfigResponse(BaseModel):
    """Schema for agent configuration response."""
    name: str
    description: str
    model: str
    provider: str
    temperature: float
    max_tokens: int
    estimated_tokens: int


class AllAgentsResponse(BaseModel):
    """Response for all agent configurations."""
    agents: Dict[str, AgentConfigResponse]
    total_estimated_tokens: int
    total_estimated_cost: float


# ============ Connector Schemas ============

class ConnectorBase(BaseModel):
    """Base schema for connectors."""
    name: str
    type: str  # github, gitlab, slack, etc.
    config: Dict[str, Any]
    is_active: bool = True


class ConnectorCreate(ConnectorBase):
    """Schema for creating a connector."""
    pass


class ConnectorResponse(ConnectorBase):
    """Schema for connector response."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============ MCP & Tool Schemas ============

class ToolBase(BaseModel):
    name: str
    description: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None

class ToolResponse(ToolBase):
    id: int
    mcp_server_id: Optional[int] = None
    
    class Config:
        from_attributes = True

class MCPServerBase(BaseModel):
    name: str
    url: str
    is_active: bool = True

class MCPServerCreate(MCPServerBase):
    auth_token: Optional[str] = None

class MCPServerResponse(MCPServerBase):
    id: int
    created_at: datetime
    tools: List[ToolResponse] = []

    class Config:
        from_attributes = True
