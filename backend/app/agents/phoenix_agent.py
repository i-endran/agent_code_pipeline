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
        
        # 0. MR Listening / Status Check
        sentinel_results = context.get("sentinel_results", {})
        pr_number = sentinel_results.get("pull_number")
        connector_id = context.get("sentinel", {}).get("connector_id")
        
        if pr_number and connector_id:
            self.logger.info(f"PHOENIX: Checking status for PR #{pr_number}...")
            from app.services.connector_service import connector_service
            from app.db.database import SessionLocal
            
            db = SessionLocal()
            try:
                # Retrieve repo info from context or config
                repo_owner = context.get("repo_owner") or "owner"
                repo_name = context.get("repo_name") or "repo"
                
                pr_data = await connector_service.get_github_mr(
                    connector_id=connector_id,
                    repo_owner=repo_owner,
                    repo_name=repo_name,
                    pull_number=pr_number,
                    db=db
                )
                
                if not pr_data.get("merged", False):
                    self.logger.info(f"PHOENIX: PR #{pr_number} is not merged yet. Waiting for webhook or manual approval.")
                    return {
                        "status": "waiting",
                        "message": f"Awaiting merge of Pull Request #{pr_number}.",
                        "pr_url": pr_data.get("html_url"),
                        "action_required": "merge_pr"
                    }
            finally:
                db.close()

        if not repo_path or not current_branch:
            # If no PR was created, we might be doing a local-only release (fallback)
            self.logger.warning("PHOENIX: No repo path or branch found. Falling back to notification only.")
            # ... existing local merge logic ...

        # 1. Merge to release branch (local git)
        merge_result = self._merge_to_release(repo_path, current_branch, release_branch)
        
        if merge_result.get("conflicts"):
            # Conflict detected — return conflict status for user resolution
            return {
                "status": "conflict",
                "message": f"Merge conflicts detected: {', '.join(merge_result['conflicts'])}",
                "conflicts": merge_result["conflicts"],
                "artifact_paths": [changelog_path] if 'changelog_path' in dir() else [],
                "summary": "Merge conflicts block release. Manual resolution required.",
                "action_required": "resolve_conflicts"
            }
        
        merge_success = merge_result.get("success", False)
        
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
            "artifact_paths": [changelog_path],
            "summary": f"Release {'completed' if merge_success else 'failed'}. Changelog generated.",
            "notification_sent": notification_sent
        }

    def _merge_to_release(self, repo_path: str, source: str, target: str) -> dict:
        """Merges source branch into target release branch. Returns merge result dict."""
        try:
            # Checkout target
            subprocess.run(["git", "checkout", target], cwd=repo_path, check=True)
            # Pull latest
            subprocess.run(["git", "pull", "origin", target], cwd=repo_path)
            # Merge
            result = subprocess.run(
                ["git", "merge", source],
                cwd=repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                # Check for merge conflicts
                conflict_result = subprocess.run(
                    ["git", "diff", "--name-only", "--diff-filter=U"],
                    cwd=repo_path,
                    capture_output=True,
                    text=True
                )
                conflicting_files = [f.strip() for f in conflict_result.stdout.strip().split("\n") if f.strip()]
                
                if conflicting_files:
                    self.logger.warning(f"PHOENIX: Merge conflicts in: {conflicting_files}")
                    # Abort the merge to leave a clean state
                    subprocess.run(["git", "merge", "--abort"], cwd=repo_path)
                    return {"success": False, "conflicts": conflicting_files}
                else:
                    self.logger.error(f"PHOENIX: Merge failed (non-conflict): {result.stderr}")
                    return {"success": False, "conflicts": []}
            
            # Push
            subprocess.run(["git", "push", "origin", target], cwd=repo_path)
            return {"success": True, "conflicts": []}
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"PHOENIX: Merge failed: {e}")
            return {"success": False, "conflicts": []}

