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

    async def get_github_mr(
        self,
        connector_id: int,
        repo_owner: str,
        repo_name: str,
        pull_number: int,
        db: Session
    ) -> Dict[str, Any]:
        """Retrieves details of a Pull Request on GitHub."""
        async with await self.get_github_client(connector_id, db) as client:
            response = await client.get(f"/repos/{repo_owner}/{repo_name}/pulls/{pull_number}")
            if response.status_code != 200:
                logger.error(f"Failed to get GitHub PR: {response.text}")
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

    async def create_gitlab_mr(
        self,
        connector_id: int,
        project_id: str,
        title: str,
        source_branch: str,
        target_branch: str,
        description: str,
        db: Session
    ) -> Dict[str, Any]:
        """Creates a Merge Request on GitLab."""
        connector = db.query(Connector).filter(Connector.id == connector_id, Connector.type == "gitlab").first()
        if not connector:
            raise ValueError(f"GitLab connector {connector_id} not found")
            
        token = connector.config.get("token")
        url = connector.config.get("url", "https://gitlab.com")
        
        async with httpx.AsyncClient(headers={"Private-Token": token}) as client:
            response = await client.post(
                f"{url}/api/v4/projects/{project_id}/merge_requests",
                json={
                    "source_branch": source_branch,
                    "target_branch": target_branch,
                    "title": title,
                    "description": description
                }
            )
            
            if response.status_code != 201:
                logger.error(f"Failed to create GitLab MR: {response.text}")
                raise RuntimeError(f"GitLab API error: {response.text}")
                
            return response.json()

    async def send_teams_notification(
        self,
        connector_id: int,
        message: str,
        db: Session
    ):
        """Sends a notification to MS Teams via Incoming Webhook."""
        connector = db.query(Connector).filter(Connector.id == connector_id, Connector.type == "teams").first()
        if not connector:
            raise ValueError(f"Teams connector {connector_id} not found")
            
        webhook_url = connector.config.get("webhook_url")
        if not webhook_url:
            raise ValueError("No webhook_url found for Teams connector")
            
        payload = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "themeColor": "0076D7",
            "summary": "Agent Notification",
            "sections": [{
                "activityTitle": "SDLC Agent Notification",
                "text": message
            }]
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(webhook_url, json=payload)
            if response.status_code != 200:
                logger.error(f"Failed to send Teams webhook: {response.text}")

    async def send_cliq_notification(
        self,
        connector_id: int,
        message: str,
        db: Session
    ):
        """Sends a notification to Zoho Cliq via Incoming Webhook."""
        connector = db.query(Connector).filter(Connector.id == connector_id, Connector.type == "cliq").first()
        if not connector:
            raise ValueError(f"Cliq connector {connector_id} not found")
            
        webhook_url = connector.config.get("webhook_url")
        if not webhook_url:
            raise ValueError("No webhook_url found for Cliq connector")
            
        async with httpx.AsyncClient() as client:
            response = await client.post(webhook_url, json={"text": message})
            if response.status_code != 200:
                logger.error(f"Failed to send Cliq webhook: {response.text}")

    async def send_generic_webhook(
        self,
        webhook_url: str,
        payload: Dict[str, Any],
        secret: Optional[str] = None
    ):
        """Sends a payload to a generic webhook URL."""
        headers = {"Content-Type": "application/json"}
        
        # Calculate signature if secret provided (HMAC SHA256)
        if secret:
            import hmac
            import hashlib
            import json
            body = json.dumps(payload).encode()
            signature = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
            headers["X-Hub-Signature-256"] = f"sha256={signature}"
            
        async with httpx.AsyncClient() as client:
            try:
                await client.post(webhook_url, json=payload, headers=headers)
            except Exception as e:
                logger.error(f"Failed to send generic webhook: {e}")

connector_service = ConnectorService()
