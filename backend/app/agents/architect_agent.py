import logging
import os
from typing import Dict, Any
from app.agents.base_agent import BaseAgent
from app.services.artifact_service import artifact_service
from pathlib import Path

logger = logging.getLogger(__name__)

class ArchitectAgent(BaseAgent):
    """Agent responsible for technical planning and codebase analysis."""
    
    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        self.logger.info("ARCHITECT: Starting codebase analysis and planning...")
        
        repo_path = context.get("repo_path")
        if not repo_path or not Path(repo_path).exists():
            self.logger.warning("ARCHITECT: No repository found or path invalid. Proceeding without repo context.")
            repo_info = "No repository context available."
        else:
            repo_info = self._analyze_repo(repo_path)

        # Build prompt using SCRIBE's output if available
        scribe_artifacts = context.get("scribe_results", {}).get("artifacts", {})
        feature_doc_path = scribe_artifacts.get("feature_doc")
        
        feature_context = ""
        if feature_doc_path:
            full_path = Path(context.get("storage_path", "./storage")) / feature_doc_path
            if full_path.exists():
                with open(full_path, "r", encoding="utf-8") as f:
                    feature_context = f.read()

        prompt = f"""
You are the ARCHITECT. Create a detailed technical implementation plan.
REPO ANALYSIS:
{repo_info}

FEATURE CONTEXT:
{feature_context}

USER NOTES:
{context.get("architect", {}).get("user_prompt", "")}

Your plan MUST specify:
1. Files to create or modify
2. Technical approach (patterns, libraries)
3. Step-by-step implementation guide for the FORGE agent
"""
        # Call LLM
        plan_content = await self.call_llm(prompt)
        
        # Save artifact
        path = artifact_service.save_artifact(self.task_id, "plan", plan_content)
        
        return {
            "status": "success",
            "message": "Technical plan generated",
            "plan_path": path,
            "repo_analyzed": bool(repo_path)
        }

    def _analyze_repo(self, repo_path: str) -> str:
        """Reads README and lists core directory structure."""
        path = Path(repo_path)
        readme_content = ""
        readme_path = path / "README.md"
        if readme_path.exists():
            with open(readme_path, "r", encoding="utf-8") as f:
                readme_content = f.read()[:2000] # Cap at 2k chars

        # List top-level files
        files = [f.name for f in path.glob("*") if f.is_file()][:20]
        dirs = [d.name for d in path.glob("*") if d.is_dir() and not d.name.startswith(".")][:10]
        
        return f"""
README Content:
{readme_content}

Directory Structure:
- Directories: {', '.join(dirs)}
- Top-level Files: {', '.join(files)}
"""
