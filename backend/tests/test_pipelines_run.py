from fastapi.testclient import TestClient
from app.main import app

def test_run_pipeline():
    with TestClient(app) as client:
        payload = {
            "repo_url": "https://github.com/example/repo",
            "branch": "main",
            "requirements": "Create a login feature",
            "agents": {
                "scribe": {"enabled": True},
                "architect": {"enabled": False},
                "forge": {"enabled": False},
                "sentinel": {"enabled": False},
                "phoenix": {"enabled": False}
            },
            "scribe_config": {
                "user_prompt": "Make it secure",
                "selected_documents": ["feature_doc", "dpia"],
                "output_format": "docx"
            }
        }

        response = client.post("/api/v1/pipelines/run", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert "task_id" in data
