import logging
import json
from pathlib import Path
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class ArtifactService:
    def __init__(self, storage_path: str = "./storage"):
        self.storage_path = Path(storage_path)
        self.artifacts_dir = self.storage_path / "artifacts"
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)

    def get_task_dir(self, task_id: str) -> Path:
        """Returns the artifact directory for a task."""
        task_dir = self.artifacts_dir / f"task_{task_id}"
        task_dir.mkdir(parents=True, exist_ok=True)
        return task_dir

    def save_artifact(self, task_id: str, artifact_type: str, content: str, filename: Optional[str] = None) -> str:
        """Saves an artifact (document, JSON, etc.) to the task directory."""
        task_dir = self.get_task_dir(task_id)
        
        if not filename:
            # Default filenames based on type
            extensions = {
                "feature_doc": "feature_document.md",
                "dpia": "dpia.md",
                "data_flow": "data_flow.md",
                "plan": "implementation_plan.md",
                "review": "review.json",
                "patch": "patch.diff"
            }
            filename = extensions.get(artifact_type, f"{artifact_type}.txt")

        file_path = task_dir / filename
        
        try:
            if isinstance(content, (dict, list)):
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(content, f, indent=2)
            else:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
            
            logger.info(f"Saved artifact {artifact_type} for task {task_id} at {file_path}")
            return str(file_path.relative_to(self.storage_path))
        except Exception as e:
            logger.error(f"Failed to save artifact {artifact_type} for task {task_id}: {e}")
            raise

    def list_artifacts(self, task_id: str) -> List[Dict]:
        """Lists all artifacts for a given task."""
        task_dir = self.get_task_dir(task_id)
        artifacts = []
        for file in task_dir.glob("*"):
            if file.is_file():
                artifacts.append({
                    "name": file.name,
                    "path": str(file.relative_to(self.storage_path)),
                    "size": file.stat().st_size
                })
        return artifacts

artifact_service = ArtifactService()
