import logging
import subprocess
from typing import Dict, Any, Optional
from app.agents.base_agent import BaseAgent
from app.services.artifact_service import artifact_service
from pathlib import Path

logger = logging.getLogger(__name__)

class PhoenixAgent(BaseAgent):
    """Agent responsible for release management and notifications."""
    
    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        self.logger.info("PHOENIX: Starting release process...")
        
        repo_path = context.get("repo_path")
        current_branch = context.get("forge_results", {}).get("branch")
        release_branch = context.get("phoenix", {}).get("release_branch", "main")
        
        if not repo_path or not current_branch:
            raise ValueError("PHOENIX: Missing repo path or branch name in context")

        # 1. Merge to release branch (local git)
        merge_success = self._merge_to_release(repo_path, current_branch, release_branch)
        
        # 2. Generate Changelog
        prompt = f"""
Generate a concise release changelog for the following changes:
TASK ID: {self.task_id}
CHANGES SUMMARY: {context.get('scribe_results', {}).get('message', 'New feature implementation')}

Format the output for a Slack message.
"""
        changelog = await self.call_llm(prompt)
        changelog_path = artifact_service.save_artifact(self.task_id, "changelog", {"changelog": changelog})
        
        # 3. Send Notifications
        notification_sent = False
        connector_id = context.get("phoenix", {}).get("connector_id")
        
        if connector_id:
            try:
                from app.services.connector_service import connector_service
                from app.db.database import SessionLocal
                
                db = SessionLocal()
                try:
                    await connector_service.send_slack_notification(
                        connector_id=connector_id,
                        message=f"🚀 *New Release Deployed!*\nTask: {self.task_id}\n\n{changelog}",
                        db=db
                    )
                    notification_sent = True
                finally:
                    db.close()
            except Exception as e:
                self.logger.error(f"PHOENIX: Failed to send Slack notification: {e}")

        return {
            "status": "success",
            "message": "Release completed and notifications sent." if notification_sent else "Release completed (Manual notification required).",
            "merge_status": "merged" if merge_success else "failed",
            "changelog_path": changelog_path,
            "notification_sent": notification_sent
        }

    def _merge_to_release(self, repo_path: str, source: str, target: str) -> bool:
        """Merges source branch into target release branch."""
        try:
            # Checkout target
            subprocess.run(["git", "checkout", target], cwd=repo_path, check=True)
            # Pull latest
            subprocess.run(["git", "pull", "origin", target], cwd=repo_path)
            # Merge
            subprocess.run(["git", "merge", source], cwd=repo_path, check=True)
            # Push (simulation if no remote access, but we try)
            subprocess.run(["git", "push", "origin", target], cwd=repo_path)
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"PHOENIX: Merge failed: {e}")
            return False
