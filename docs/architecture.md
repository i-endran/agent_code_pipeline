# System Architecture

## Overview

The SDLC Agent Pipeline Tool orchestrates 5 AI agents (powered by Google Gemini) to automate software development workflows from requirements to release, with full audit trail capabilities.

## Architecture Diagram

```
                                    ┌─────────────────┐
                                    │   Frontend      │
                                    │  (React + TW)   │ ← Phase 3
                                    └────────┬────────┘
                                             │ HTTP/WS
                                             ▼
┌────────────────────────────────────────────────────────────────┐
│                        FastAPI Backend                         │
├──────────────┬─────────────────┬─────────────────┬────────────┤
│   REST API   │   WebSocket     │   Swagger UI    │   Config   │
│  /api/*      │   /ws/status    │    /docs        │   Loader   │
└──────┬───────┴────────┬────────┴─────────────────┴────────────┘
       │                │
       ▼                │
┌──────────────┐        │         ┌─────────────────────────────┐
│  PostgreSQL  │        │         │         RabbitMQ            │
│  (Tasks DB)  │        │         │    (Persistent Queues)      │
└──────────────┘        │         └──────────────┬──────────────┘
                        │                        │
                        ▼                        ▼
              ┌─────────────────────────────────────────────────┐
              │              Celery Worker Pool                 │
              ├─────────┬─────────┬─────────┬─────────┬─────────┤
              │Worker 1 │Worker 2 │Worker 3 │Worker 4 │Worker 5 │
              └────┬────┴────┬────┴────┬────┴────┬────┴────┬────┘
                   │         │         │         │         │
                   ▼         ▼         ▼         ▼         ▼
              ┌─────────────────────────────────────────────────┐
              │                  Agent Layer                    │
              │  SCRIBE → ARCHITECT → FORGE → SENTINEL →        │
              │                         PHOENIX                 │
              │           (All with State Capture)              │
              └─────────────────────────────────────────────────┘
                                     │
                                     ▼
              ┌─────────────────────────────────────────────────┐
              │              Google Gemini API                  │
              │   gemini-2.0-flash  │  gemini-2.0-pro-exp       │
              └─────────────────────────────────────────────────┘
                                     │
                                     ▼
              ┌─────────────────────────────────────────────────┐
              │                Storage Layer                    │
              │  Repos │ Artifacts │ Audit │ Patches │ Logs     │
              └─────────────────────────────────────────────────┘
```

## Component Details

### Frontend (Phase 3 - In Progress)
- **Technology**: React 18 + Tailwind CSS 3 + Vite
- **Features**: 
  - Sidebar navigation (Pipeline, Connectors, Extensions, Models)
  - Agent pipeline visualization with modals
  - Real-time status updates via WebSocket
  - Dark mode, responsive design
- **Previous**: HTML5 + Bootstrap 5 + Vanilla JS (Phase 1)

### Backend (FastAPI)
- **Framework**: FastAPI with automatic OpenAPI docs
- **Database**: SQLAlchemy ORM (SQLite dev / PostgreSQL prod)
- **Real-time**: WebSocket for live status updates
- **Config**: Pydantic Settings with `.env` support
- **New Models** (Phase 2):
  - `Repository`: Track cloned repos per task
  - `TaskArtifact`: Store generated documents
  - `AgentExecutionLog`: Full agent state snapshots

### Task Queue (Celery + RabbitMQ)
- **Broker**: RabbitMQ with persistent queues
- **Crash Recovery**: `CELERY_TASK_ACKS_LATE=True`
- **Concurrency**: Configurable worker pool (default: 5)
- **Orchestration**: Sequential agent execution with context passing

### LLM Service (Google Gemini)
- **Models**: 
  - `gemini-2.0-flash`: SCRIBE, ARCHITECT, FORGE, PHOENIX
  - `gemini-2.0-pro-exp-02-05`: ARCHITECT, SENTINEL
- **Config**: Per-agent model selection from `agents.yaml`
- **Tracking**: Token consumption per request (future)

### Storage Services (Phase 2B)
- **RepoService**: Clone, branch management, pruning
- **ArtifactService**: Save/list documents, plans, reviews
- **AuditService**: Capture agent states, link to Git commits
- **Directory Structure**:
  ```
  backend/storage/
  ├── logs/              # Structured logs (daily rotation)
  ├── repos/             # Cloned repositories (repo_{id})
  ├── artifacts/         # Generated documents (task_{id})
  ├── audit/             # Agent state snapshots (JSON)
  └── patches/           # Code review diffs
  ```

## Data Flow

### Pipeline Execution
```
1. User submits pipeline config via UI
2. Backend validates and creates Task record
3. Repository cloned to storage/repos/repo_{id}
4. Task dispatched to Celery queue
5. Worker executes agents sequentially:
   - Each agent auto-captures state snapshot
   - SCRIBE → generates documents
   - ARCHITECT → analyzes repo, creates plan
   - FORGE → implements code, commits with metadata
   - SENTINEL → reviews, creates MR or routes back
   - PHOENIX → merges, notifies stakeholders
6. WebSocket pushes status updates to UI
7. Artifacts saved to storage/artifacts/task_{id}/
8. Audit trail queryable via /api/audit/*
```

### Context Persistence
```python
class PipelineContext:
    task_id: str
    current_stage: int  # 1-5 (HERALD removed)
    artifacts: dict     # Agent outputs
    config: dict        # User inputs
    repo_path: str      # Cloned repository path
    branch_name: str    # Feature branch
```

### Agent State Auditing (Phase 2D)
Every agent execution captures:
- Model, temperature, max_tokens, provider
- Guardrails, policies, enforcement prompts
- Tools list, user prompt
- Execution timestamp, status
- Git commit hash (for FORGE)

**Query APIs**:
- `GET /api/audit/task/{task_id}` - All agent executions
- `GET /api/audit/state/{state_id}` - Full config snapshot
- `GET /api/audit/commit/{commit_hash}` - Trace commit to agent

## Scalability

### Current (Phase 2)
- Single machine, multiple Celery workers
- SQLite for development
- Local file storage for repos/artifacts

### Future Options
| Scale | Infrastructure |
|-------|----------------|
| Small | Docker Compose (5-10 workers) |
| Medium | Docker Swarm (10-50 workers) |
| Large | Kubernetes (50+ pods) |

## Security Considerations

> **Note**: Authentication disabled for internal use (Phase 1-2)

Future phases will add:
- JWT authentication (Phase 5)
- Role-based access control
- API key management for LLM providers
- Audit logging (✅ Implemented in Phase 2D)
- Encrypted storage for sensitive data

## Agent Workflow

```mermaid
graph LR
    A[SCRIBE] -->|Feature Doc| B[ARCHITECT]
    B -->|Implementation Plan| C[FORGE]
    C -->|Code Changes| D[SENTINEL]
    D -->|Review Pass| E[PHOENIX]
    D -->|Review Fail| C
    E -->|Release| F[Done]
    
    style A fill:#3b82f6
    style B fill:#3b82f6
    style C fill:#3b82f6
    style D fill:#3b82f6
    style E fill:#3b82f6
```

## Technology Evolution

| Phase | Frontend | Backend | LLM | Storage |
|-------|----------|---------|-----|---------|
| 1 | HTML+Bootstrap | FastAPI+Celery | - | SQLite |
| 2A-C | HTML+Bootstrap | + Logging, Agents | Gemini | + File Storage |
| 2D | HTML+Bootstrap | + Audit Trail | Gemini | + Audit Snapshots |
| 3 | **React+Tailwind** | Same | Gemini | Same |
| 4 | React+Tailwind | + Connectors, MCP | Gemini | Same |
| 5 | React+Tailwind | + Human-in-Loop | Gemini | Same |
| 6 | React+Tailwind | + PHOENIX Full | Gemini | Same |
