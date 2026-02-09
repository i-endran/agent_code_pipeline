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
            # Simulate MR creation
            mr_link = f"https://github.com/simulated/repo/pull/{self.task_id}"
            return {
                "status": "success",
                "message": "Review approved. MR created.",
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
