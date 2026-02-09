import logging
import httpx
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.models import Connector

logger = logging.getLogger(__name__)

class ConnectorService:
    """
    Service for managing external platform connectors (GitHub, Slack, etc.).
    Handles API interactions with these platforms.
    """
    
    async def get_github_client(self, connector_id: int, db: Session):
        """Returns a configured GitHub client for a connector."""
        connector = db.query(Connector).filter(Connector.id == connector_id, Connector.type == "github").first()
        if not connector:
            raise ValueError(f"GitHub connector {connector_id} not found")
        
        token = connector.config.get("token")
        if not token:
            raise ValueError(f"No token found for GitHub connector {connector_id}")
            
        return httpx.AsyncClient(
            base_url="https://api.github.com",
            headers={
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json"
            }
        )

    async def create_github_mr(
        self, 
        connector_id: int, 
        repo_owner: str, 
        repo_name: str, 
        title: str, 
        head: str, 
        base: str, 
        body: str,
        db: Session
    ) -> Dict[str, Any]:
        """Creates a Pull Request on GitHub."""
        async with await self.get_github_client(connector_id, db) as client:
            response = await client.post(
                f"/repos/{repo_owner}/{repo_name}/pulls",
                json={
                    "title": title,
                    "head": head,
                    "base": base,
                    "body": body
                }
            )
            
            if response.status_code != 201:
                logger.error(f"Failed to create GitHub PR: {response.text}")
                raise RuntimeError(f"GitHub API error: {response.text}")
                
            return response.json()

    async def send_slack_notification(
        self, 
        connector_id: int, 
        message: str, 
        db: Session,
        channel: Optional[str] = None
    ):
        """Sends a notification to Slack via Webhook or App API."""
        connector = db.query(Connector).filter(Connector.id == connector_id, Connector.type == "slack").first()
        if not connector:
            raise ValueError(f"Slack connector {connector_id} not found")
            
        webhook_url = connector.config.get("webhook_url")
        if webhook_url:
            async with httpx.AsyncClient() as client:
                response = await client.post(webhook_url, json={"text": message})
                if response.status_code not in [200, 201]:
                    logger.error(f"Failed to send Slack webhook: {response.text}")
        else:
            # Fallback to API if token is present
            token = connector.config.get("token")
            if not token:
                raise ValueError(f"No webhook or token found for Slack connector {connector_id}")
                
            async with httpx.AsyncClient(
                base_url="https://slack.com/api",
                headers={"Authorization": f"Bearer {token}"}
            ) as client:
                response = await client.post(
                    "/chat.postMessage",
                    json={
                        "channel": channel or connector.config.get("default_channel"),
                        "text": message
                    }
                )
                if not response.json().get("ok"):
                    logger.error(f"Failed to send Slack API message: {response.text}")

connector_service = ConnectorService()
