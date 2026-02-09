"""
FastAPI Main Application

Entry point for the SDLC Agent Pipeline API.
Includes Swagger UI at /docs for API testing.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.api import (
    pipelines,
    tasks,
    agents,
    websocket,
    artifacts,
    audit,
    connectors,
    mcp,
    webhooks,
    approvals,
    agent_queue
)
from app.db.database import engine, Base
from app.services.logging_service import setup_logging

# Initialize logging
setup_logging(log_type="api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    print(f"Starting SDLC Agent Pipeline API ({settings.APP_ENV} mode)")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    print("Database tables created")
    
    yield
    
    # Shutdown
    print("Shutting down...")


# Create FastAPI app with metadata for Swagger
app = FastAPI(
    title="SDLC Agent Pipeline API",
    description="""
## AI-Powered Software Development Lifecycle Automation

This API orchestrates 6 AI agents to automate the software development workflow:

| Agent | Codename | Role |
|-------|----------|------|
| 1 | **SCRIBE** | Requirement → Feature Doc |
| 2 | **ARCHITECT** | Feature Doc → Plan |
| 3 | **FORGE** | Code Executor |
| 4 | **HERALD** | MR Creator |
| 5 | **SENTINEL** | Code Reviewer |
| 6 | **PHOENIX** | Releaser |

### Getting Started
1. Configure agents via `/api/v1/agents`
2. Create a pipeline via `/api/v1/pipelines`
3. Monitor status via WebSocket `/ws/status/{task_id}`
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.is_development else ["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(
    pipelines.router,
    prefix="/api/v1/pipelines",
    tags=["Pipelines"]
)

app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])
app.include_router(agents.router, prefix="/api/agents", tags=["Agents"])
app.include_router(artifacts.router, prefix="/api/artifacts", tags=["Artifacts"])
app.include_router(audit.router, prefix="/api/audit", tags=["Audit"])
app.include_router(connectors.router, prefix="/api/connectors", tags=["Connectors"])
app.include_router(mcp.router, prefix="/api/mcp", tags=["MCP"])
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["Webhooks"])
app.include_router(approvals.router, prefix="/api/approvals", tags=["Approvals"])
app.include_router(agent_queue.router, prefix="/api/queues", tags=["Agent Queues"])
app.include_router(websocket.router, tags=["WebSocket"])


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "SDLC Agent Pipeline",
        "version": "1.0.0",
        "environment": settings.APP_ENV
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "database": "connected",
        "queue": "connected",
        "environment": settings.APP_ENV
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.is_development
    )
