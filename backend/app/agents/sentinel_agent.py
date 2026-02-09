import logging
import subprocess
from typing import Dict, Any
from app.agents.base_agent import BaseAgent
from app.services.artifact_service import artifact_service
from pathlib import Path

logger = logging.getLogger(__name__)

class SentinelAgent(BaseAgent):
    """Agent responsible for code review and MR creation."""
    
    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        self.logger.info("SENTINEL: Starting code review...")
        
        repo_path = context.get("repo_path")
        branch_name = context.get("forge_results", {}).get("branch")
        
        if not repo_path or not branch_name:
            raise ValueError("SENTINEL: Missing repo path or branch name in context")

        # 1. Generate local diff patch
        diff_content = self._get_diff(repo_path, branch_name)
        patch_path = artifact_service.save_artifact(self.task_id, "patch", diff_content)
        
        # 2. Review the diff
        prompt = f"""
Review the following code changes for security, quality, and adherence to requirements:
DIFF:
{diff_content[:10000]} # Cap for LLM context

USER NOTES: {context.get("sentinel", {}).get("user_prompt", "")}

Decide if the changes are APPROVED or REJECTED.
If REJECTED, provide specific fix instructions for the FORGE agent.
"""
        review_result = await self.call_llm(prompt)
        
        # 3. Persist review
        review_path = artifact_service.save_artifact(self.task_id, "review", {"review": review_result})
        
        is_approved = "APPROVED" in review_result.upper()
        
        if is_approved:
            self.logger.info("SENTINEL: Changes APPROVED. Creating MR...")
            
            mr_url = None
            connector_id = context.get("sentinel", {}).get("connector_id")
            
            if connector_id:
                try:
                    from app.services.connector_service import connector_service
                    from app.db.database import SessionLocal
                    
                    db = SessionLocal()
                    try:
                        # Extract owner/repo from repo_url if possible, or use config
                        repo_owner = context.get("scribe", {}).get("repo_owner", "owner")
                        repo_name = context.get("scribe", {}).get("repo_name", "repo")
                        
                        mr_data = await connector_service.create_github_mr(
                            connector_id=connector_id,
                            repo_owner=repo_owner,
                            repo_name=repo_name,
                            title=f"[AUTO] {context.get('task_id')}",
                            head=branch_name,
                            base="main",
                            body=review_result,
                            db=db
                        )
                        mr_url = mr_data.get("html_url")
                    finally:
                        db.close()
                except Exception as e:
                    self.logger.error(f"SENTINEL: Failed to create GitHub MR: {e}")
            
            mr_link = mr_url or f"https://github.com/simulated/repo/pull/{self.task_id}"
            
            return {
                "status": "success",
                "message": "Review approved. MR created." if mr_url else "Review approved (Simulation).",
                "review_path": review_path,
                "patch_path": patch_path,
                "mr_url": mr_link,
                "action": "merging"
            }
        else:
            self.logger.warning("SENTINEL: Changes REJECTED. Routing back to FORGE.")
            return {
                "status": "fix_needed",
                "message": "Review rejected. Fixes required.",
                "review_path": review_path,
                "action": "reworking"
            }

    def _get_diff(self, repo_path: str, branch_name: str, base_branch: str = "main") -> str:
        """Generates a diff between the current branch and the base branch."""
        try:
            result = subprocess.run(
                ["git", "diff", base_branch, branch_name],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to generate diff: {e}")
            return f"Error generating diff: {e}"
