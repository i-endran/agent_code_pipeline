# System Architecture

## Overview

The SDLC Agent Pipeline Tool orchestrates 6 AI agents to automate software development workflows from requirements to release.

## Architecture Diagram

```
                                    ┌─────────────────┐
                                    │   Frontend      │
                                    │  (Bootstrap)    │
                                    └────────┬────────┘
                                             │ HTTP/WS
                                             ▼
┌────────────────────────────────────────────────────────────────┐
│                        FastAPI Backend                         │
├──────────────┬─────────────────┬─────────────────┬────────────┤
│   REST API   │   WebSocket     │   Swagger UI    │   Config   │
│  /api/v1/*   │   /ws/status    │    /docs        │   Loader   │
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
              │  SCRIBE → ARCHITECT → FORGE → HERALD →          │
              │                    SENTINEL → PHOENIX           │
              └─────────────────────────────────────────────────┘
                                     │
                                     ▼
              ┌─────────────────────────────────────────────────┐
              │              LiteLLM Service                    │
              │   OpenAI  │  Anthropic  │  Google Gemini        │
              └─────────────────────────────────────────────────┘
```

## Component Details

### Frontend (Phase 1)
- **Technology**: HTML5, Bootstrap 5, Vanilla JS
- **Features**: Agent pipeline visualization, modal forms, status tracking
- **Future**: React + TypeScript + React Flow (Phase 4)

### Backend (FastAPI)
- **Framework**: FastAPI with automatic OpenAPI docs
- **Database**: SQLAlchemy ORM (SQLite dev / PostgreSQL prod)
- **Real-time**: WebSocket for live status updates
- **Config**: Pydantic Settings with `.env` support

### Task Queue (Celery + RabbitMQ)
- **Broker**: RabbitMQ with persistent queues
- **Crash Recovery**: `CELERY_TASK_ACKS_LATE=True`
- **Concurrency**: Configurable worker pool (default: 5)

### LLM Service (LiteLLM)
- **Providers**: OpenAI, Anthropic, Google Gemini
- **Config**: Per-agent model selection from `agents.yaml`
- **Tracking**: Token consumption per request

## Data Flow

### Pipeline Execution
```
1. User submits pipeline config via UI
2. Backend validates and creates Task record
3. Task dispatched to Celery queue
4. Worker picks up task, executes agents sequentially
5. Each agent writes output to context store
6. WebSocket pushes status updates to UI
7. On completion, final artifacts stored in DB
```

### Context Persistence
```python
class PipelineContext:
    task_id: str
    current_stage: int  # 1-6
    artifacts: dict     # Agent outputs
    config: dict        # User inputs
    token_usage: dict   # Per-agent tokens
```

## Scalability

### Current (Phase 1)
- Single machine, multiple Celery workers
- SQLite for development

### Future Options
| Scale | Infrastructure |
|-------|---------------|
| Small | Docker Compose (5-10 workers) |
| Medium | Docker Swarm (10-50 workers) |
| Large | Kubernetes (50+ pods) |

## Security Considerations

> **Note**: Authentication disabled for internal use (Phase 1)

Future phases will add:
- JWT authentication
- Role-based access control
- API key management for LLM providers
- Audit logging
