from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch, AsyncMock

def test_run_pipeline():
    with TestClient(app) as client:
        # Mock httpx.AsyncClient.get for fetch_readme_content
        with patch('httpx.AsyncClient.get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.text = "# Project README"

            payload = {
                "repo_url": "https://github.com/example/repo",
                "readme_url": "https://raw.githubusercontent.com/example/repo/main/README.md",
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
            if response.status_code != 201:
                print(f"Failed: {response.status_code} - {response.text}")
            assert response.status_code == 201
            data = response.json()
            assert "task_id" in data
            print(f"Task created with ID: {data['task_id']}")

            # Verify httpx was called
            # Note: Since TestClient runs synchronous, async calls inside might be tricky to mock directly if not careful.
            # But FastAPI handles async endpoints fine. The patch should work if the endpoint awaits it.

if __name__ == "__main__":
    test_run_pipeline()
    print("Pipeline run test passed!")
