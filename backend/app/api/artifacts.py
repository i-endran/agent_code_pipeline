from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import TaskArtifact, Task
from app.services.artifact_service import artifact_service
from pathlib import Path
import os

router = APIRouter()

@router.get("/{task_id}")
async def list_task_artifacts(task_id: str, db: Session = Depends(get_db)):
    """List all artifacts for a task."""
    artifacts = db.query(TaskArtifact).filter(TaskArtifact.task_id == task_id).all()
    return artifacts

@router.get("/{task_id}/{artifact_id}/download")
async def download_artifact(task_id: str, artifact_id: int, db: Session = Depends(get_db)):
    """Download a specific artifact."""
    artifact = db.query(TaskArtifact).filter(
        TaskArtifact.id == artifact_id,
        TaskArtifact.task_id == task_id
    ).first()
    
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")
    
    # Check if file exists on disk
    storage_path = Path("./storage")
    file_path = storage_path / artifact.file_path
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"File not found on disk: {artifact.file_path}")
    
    return FileResponse(
        path=file_path,
        filename=os.path.basename(artifact.file_path),
        media_type='application/octet-stream'
    )
