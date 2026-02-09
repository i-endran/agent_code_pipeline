"""
Unit Tests for Pipeline API

Tests the pipeline CRUD operations and validation logic.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.db.database import Base, engine, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_db():
    """Create tables before each test."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client():
    """Create test client with overridden database."""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


class TestHealthEndpoints:
    """Tests for health check endpoints."""
    
    def test_root_health(self, client):
        """Test root endpoint returns healthy status."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
    
    def test_health_check(self, client):
        """Test detailed health check."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestPipelineAPI:
    """Tests for pipeline CRUD operations."""
    
    def test_create_pipeline_minimal(self, client):
        """Test creating a pipeline with minimal config."""
        payload = {
            "name": "Test Pipeline",
            "description": "A test pipeline",
            "agent_configs": {
                "scribe": {"enabled": True, "requirement_text": "Test requirement"},
                "architect": {"enabled": False},
                "forge": {"enabled": False},
                "herald": {"enabled": False},
                "sentinel": {"enabled": False},
                "phoenix": {"enabled": False}
            }
        }
        
        response = client.post("/api/v1/pipelines/", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Pipeline"
        assert "scribe" in data["enabled_agents"]
    
    def test_create_pipeline_sequential_validation(self, client):
        """Test that agents must be enabled sequentially."""
        # Try to enable forge without scribe and architect
        payload = {
            "name": "Invalid Pipeline",
            "agent_configs": {
                "scribe": {"enabled": False},
                "architect": {"enabled": False},
                "forge": {"enabled": True},  # Should fail
                "herald": {"enabled": False},
                "sentinel": {"enabled": False},
                "phoenix": {"enabled": False}
            }
        }
        
        response = client.post("/api/v1/pipelines/", json=payload)
        assert response.status_code == 400
        assert "sequentially" in response.json()["detail"].lower()
    
    def test_create_pipeline_no_agents(self, client):
        """Test that at least one agent must be enabled."""
        payload = {
            "name": "Empty Pipeline",
            "agent_configs": {
                "scribe": {"enabled": False},
                "architect": {"enabled": False},
                "forge": {"enabled": False},
                "herald": {"enabled": False},
                "sentinel": {"enabled": False},
                "phoenix": {"enabled": False}
            }
        }
        
        response = client.post("/api/v1/pipelines/", json=payload)
        assert response.status_code == 400
        assert "at least one" in response.json()["detail"].lower()
    
    def test_list_pipelines(self, client):
        """Test listing pipelines."""
        # Create a pipeline first
        payload = {
            "name": "List Test",
            "agent_configs": {
                "scribe": {"enabled": True},
                "architect": {"enabled": False},
                "forge": {"enabled": False},
                "herald": {"enabled": False},
                "sentinel": {"enabled": False},
                "phoenix": {"enabled": False}
            }
        }
        client.post("/api/v1/pipelines/", json=payload)
        
        response = client.get("/api/v1/pipelines/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
    
    def test_get_pipeline_by_id(self, client):
        """Test getting a specific pipeline."""
        # Create a pipeline
        payload = {
            "name": "Get Test",
            "agent_configs": {
                "scribe": {"enabled": True},
                "architect": {"enabled": True},
                "forge": {"enabled": False},
                "herald": {"enabled": False},
                "sentinel": {"enabled": False},
                "phoenix": {"enabled": False}
            }
        }
        create_response = client.post("/api/v1/pipelines/", json=payload)
        pipeline_id = create_response.json()["id"]
        
        response = client.get(f"/api/v1/pipelines/{pipeline_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Get Test"
        assert "scribe" in data["enabled_agents"]
        assert "architect" in data["enabled_agents"]
    
    def test_get_pipeline_not_found(self, client):
        """Test getting a non-existent pipeline."""
        response = client.get("/api/v1/pipelines/9999")
        assert response.status_code == 404
    
    def test_delete_pipeline(self, client):
        """Test deleting a pipeline."""
        # Create a pipeline
        payload = {
            "name": "Delete Test",
            "agent_configs": {
                "scribe": {"enabled": True},
                "architect": {"enabled": False},
                "forge": {"enabled": False},
                "herald": {"enabled": False},
                "sentinel": {"enabled": False},
                "phoenix": {"enabled": False}
            }
        }
        create_response = client.post("/api/v1/pipelines/", json=payload)
        pipeline_id = create_response.json()["id"]
        
        # Delete it
        response = client.delete(f"/api/v1/pipelines/{pipeline_id}")
        assert response.status_code == 204
        
        # Verify it's gone
        response = client.get(f"/api/v1/pipelines/{pipeline_id}")
        assert response.status_code == 404


class TestAgentsAPI:
    """Tests for agent configuration endpoints."""
    
    def test_list_agents(self, client):
        """Test listing all agents."""
        response = client.get("/api/v1/agents/")
        assert response.status_code == 200
        data = response.json()
        assert "agents" in data
        assert "total_estimated_tokens" in data
        assert "total_estimated_cost" in data
    
    def test_get_agent(self, client):
        """Test getting a specific agent."""
        response = client.get("/api/v1/agents/scribe")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "scribe"
        assert "name" in data
        assert "model" in data
    
    def test_get_agent_not_found(self, client):
        """Test getting a non-existent agent."""
        response = client.get("/api/v1/agents/nonexistent")
        assert response.status_code == 404


class TestTasksAPI:
    """Tests for task management endpoints."""
    
    def test_list_running_tasks_empty(self, client):
        """Test listing running tasks when none exist."""
        response = client.get("/api/v1/tasks/running")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_task_not_found(self, client):
        """Test getting a non-existent task."""
        response = client.get("/api/v1/tasks/9999")
        assert response.status_code == 404
    
    def test_token_dashboard(self, client):
        """Test token dashboard endpoint."""
        response = client.get("/api/v1/tasks/dashboard/tokens")
        assert response.status_code == 200
        data = response.json()
        assert "total_tokens" in data
        assert "total_cost" in data
        assert "daily_usage" in data
