import hmac
import hashlib
import json
import logging
from typing import Dict, Any
from fastapi import APIRouter, Request, Header, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import Connector, Task, TaskStatus
from app.utils.task_utils import send_task_update

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/github")
async def github_webhook(
    request: Request,
    x_github_event: str = Header(None),
    x_hub_signature_256: str = Header(None),
    db: Session = Depends(get_db)
):
    """Handles incoming GitHub webhooks."""
    payload = await request.body()
    
    # Optional: Verify signature if secret is configured in Connector
    # For now, we'll look for a GitHub connector to find the secret
    connector = db.query(Connector).filter(Connector.type == "github", Connector.is_active == True).first()
    
    if connector and "webhook_secret" in connector.config:
        secret = connector.config["webhook_secret"]
        if not verify_github_signature(payload, x_hub_signature_256, secret):
            logger.warning("GitHub webhook signature verification failed")
            raise HTTPException(status_code=401, detail="Invalid signature")

    data = json.loads(payload)
    event_type = x_github_event
    
    logger.info(f"Received GitHub event: {event_type}")
    
    if event_type == "pull_request":
        action = data.get("action")
        pr = data.get("pull_request")
        merged = pr.get("merged", False)
        
        if action == "closed" and merged:
            # PR was merged! Find the associated task.
            # We can use the PR URL or a custom tracking ID in the body/branch name.
            pr_url = pr.get("html_url")
            await handle_mr_merged(pr_url, db)
            
    return {"status": "accepted"}

@router.post("/gitlab")
async def gitlab_webhook(
    request: Request,
    x_gitlab_token: str = Header(None),
    db: Session = Depends(get_db)
):
    """Handles incoming GitLab webhooks."""
    data = await request.json()
    event_type = data.get("object_kind")
    
    connector = db.query(Connector).filter(Connector.type == "gitlab", Connector.is_active == True).first()
    if connector and "webhook_token" in connector.config:
        if x_gitlab_token != connector.config["webhook_token"]:
            raise HTTPException(status_code=401, detail="Invalid token")

    if event_type == "merge_request":
        attr = data.get("object_attributes", {})
        state = attr.get("state")
        action = attr.get("action")
        
        if state == "merged":
            mr_url = attr.get("url")
            await handle_mr_merged(mr_url, db)

    return {"status": "accepted"}

def verify_github_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verifies HMAC hex digest of the payload."""
    if not signature:
        return False
    sha_name, signature = signature.split('=')
    if sha_name != 'sha256':
        return False
    mac = hmac.new(secret.encode(), msg=payload, digestmod=hashlib.sha256)
    return hmac.compare_digest(mac.hexdigest(), signature)

async def handle_mr_merged(mr_url: str, db: Session):
    """Logic to trigger Phoenix or finish task when MR is merged."""
    # Find task associated with this MR
    # In a real app, we'd have an AgentExecutionLog or Task metadata for the PR
    # For now, we'll scan tasks in 'AWAITING_REVIEW' or 'PROCESSING'
    task = db.query(Task).filter(
        Task.status.in_([TaskStatus.PROCESSING, TaskStatus.AWAITING_REVIEW])
    ).first() # Simplified search
    
    if task:
        logger.info(f"MR {mr_url} merged. Resuming task {task.id} for PHOENIX stage.")
        # Trigger the Phoenix agent or move task to completed if already done
        send_task_update(task.id, {
            "message": "PR Merged! Triggering automated release (PHOENIX)...",
            "progress": 95
        })
        # Note: In a production app, we would re-run the Celery task 
        # but skip to the Phoenix stage.
