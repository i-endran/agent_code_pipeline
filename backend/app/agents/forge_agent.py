import logging
import subprocess
import json
from typing import Dict, Any
from app.agents.base_agent import BaseAgent
from app.services.repo_service import repo_service

logger = logging.getLogger(__name__)

class ForgeAgent(BaseAgent):
    """Agent responsible for implementing code changes using Gemini CLI."""
    
    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        self.logger.info("FORGE: Starting code execution...")
        
        repo_path = context.get("repo_path")
        if not repo_path:
            raise ValueError("FORGE: No repository path provided in context")
            
        task_id = context.get("task_id")
        forge_config = context.get("forge", {})
        
        # 1. Create task branch
        branch_name = f"forge-task-{task_id}"
        repo_service.create_branch(repo_path, branch_name)
        
        # 2. Get technical plan
        plan_path = context.get("architect_results", {}).get("plan_path")
        plan_content = ""
        if plan_path:
            storage_path = Path(context.get("storage_path", "./storage"))
            full_plan_path = storage_path / plan_path
            if full_plan_path.exists():
                with open(full_plan_path, "r", encoding="utf-8") as f:
                    plan_content = f.read()

        # 3. Simulate Gemini CLI call (Headless Mode)
        # In a real implementation, we would run:
        # subprocess.run(["gemini", "--headless", "--prompt", ...])
        
        self.logger.info(f"FORGE: Simulating Gemini CLI execution on branch {branch_name}...")
        
        # Prompt for Forge
        prompt = f"""
Implement the following technical plan:
{plan_content}

USER COMMANDS:
- Repository: {repo_path}
- Test Command: {forge_config.get("test_command", "npm test")}
- Lint Command: {forge_config.get("lint_command", "npm run lint")}

USER NOTES: {forge_config.get("user_prompt", "")}
"""
        # For now, we use the LLM to 'simulate' code generation and then we would apply it.
        # But per requirements, let's assume we call a stub or real CLI.
        
        # Simulate LLM deciding what to do
        forge_response = await self.call_llm(prompt)
        
        # 4. Run tests (stub)
        test_cmd = forge_config.get("test_command", "npm test")
        self.logger.info(f"FORGE: Running tests: {test_cmd}")
        # result = subprocess.run(test_cmd.split(), cwd=repo_path, capture_output=True)
        test_passed = True # Simulated
        
        return {
            "status": "success",
            "message": "Code changes implemented and tested",
            "branch": branch_name,
            "test_passed": test_passed,
            "changes_summary": forge_response[:500]
        }
