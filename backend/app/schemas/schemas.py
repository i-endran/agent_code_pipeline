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
    approval_required: bool = False
    approval_timeout_minutes: int = 60


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

class PipelineRunScribeConfig(BaseModel):
    user_prompt: Optional[str] = None
    selected_documents: List[str] = ["feature_doc"]
    output_format: str = "markdown"

class PipelineRunRequest(BaseModel):
    """Schema for running a pipeline directly."""
    repo_url: str
    branch: str = "main"
    requirements: str
    agents: Dict[str, Dict[str, bool]]
    scribe_config: Optional[PipelineRunScribeConfig] = None

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


# ============ Approval Schemas (Phase 5: HITL) ============

class ApprovalCheckpointEnum(str, Enum):
    """Approval checkpoint enum for API."""
    SCRIBE_OUTPUT = "scribe_output"
    ARCHITECT_PLAN = "architect_plan"
    FORGE_CODE = "forge_code"
    SENTINEL_REVIEW = "sentinel_review"
    PHOENIX_RELEASE = "phoenix_release"


class ApprovalStatusEnum(str, Enum):
    """Approval status enum for API."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    TIMEOUT = "timeout"


class ApprovalActionCreate(BaseModel):
    """Schema for creating an approval action (approve/reject)."""
    action: ApprovalStatusEnum
    comment: Optional[str] = None
    feedback: Optional[Dict[str, Any]] = None
    user_name: Optional[str] = "System"


class ApprovalActionResponse(BaseModel):
    """Schema for approval action response."""
    id: int
    approval_request_id: int
    action: ApprovalStatusEnum
    user_name: str
    comment: Optional[str]
    feedback: Optional[Dict[str, Any]]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ApprovalRequestResponse(BaseModel):
    """Schema for approval request response."""
    id: int
    task_id: str
    checkpoint: ApprovalCheckpointEnum
    agent_name: str
    status: ApprovalStatusEnum
    artifact_paths: List[str]
    summary: Optional[str]
    details: Optional[Dict[str, Any]]
    created_at: datetime
    timeout_at: Optional[datetime]
    resolved_at: Optional[datetime]
    auto_approve_on_timeout: bool
    priority: int = 5
    actions: List[ApprovalActionResponse] = []
    
    class Config:
        from_attributes = True


class ApprovalDashboardResponse(BaseModel):
    """Dashboard view of approval requests."""
    pending_count: int
    approved_count: int
    rejected_count: int
    timeout_count: int
    pending_requests: List[ApprovalRequestResponse]
    recent_actions: List[ApprovalActionResponse]


class NotificationPreferenceCreate(BaseModel):
    """Schema for creating notification preferences."""
    user_id: str
    email_enabled: bool = True
    email_address: Optional[str] = None
    slack_enabled: bool = False
    slack_webhook_url: Optional[str] = None
    teams_enabled: bool = False
    teams_webhook_url: Optional[str] = None
    notify_on_request: bool = True
    notify_on_timeout_warning: bool = True
    timeout_warning_minutes: int = 15


class NotificationPreferenceResponse(BaseModel):
    """Schema for notification preference response."""
    id: int
    user_id: str
    email_enabled: bool
    email_address: Optional[str]
    slack_enabled: bool
    teams_enabled: bool
    notify_on_request: bool
    notify_on_timeout_warning: bool
    timeout_warning_minutes: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# ============ Webhook Schemas ============

class WebhookBase(BaseModel):
    name: str
    url: str
    secret: Optional[str] = None
    events: List[str] = []
    platform: str = "custom"
    is_active: bool = True

class WebhookCreate(WebhookBase):
    pass

class WebhookResponse(WebhookBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ============ Agent Mapping Schemas ============

class AgentConnectorMappingResponse(BaseModel):
    id: int
    agent_stage: AgentStageEnum
    connector_id: Optional[int]
    webhook_id: Optional[int]
    is_active: bool

    class Config:
        from_attributes = True
