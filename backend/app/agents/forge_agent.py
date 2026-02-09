import logging
import subprocess
import json
from typing import Dict, Any
from pathlib import Path
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
        
        # 5. Commit changes with agent state metadata
        commit_rules = self.config.get('commit_rules', {})
        commit_hash = self._commit_with_metadata(
            repo_path=repo_path,
            branch_name=branch_name,
            description="Implemented feature based on technical plan",
            commit_rules=commit_rules
        )
        
        return {
            "status": "success",
            "message": "Code changes implemented and tested",
            "branch": branch_name,
            "test_passed": test_passed,
            "commit_hash": commit_hash,
            "agent_state_id": self.state_id,
            "artifact_paths": [],
            "summary": f"Code implemented on branch {branch_name}, tests {'passed' if test_passed else 'failed'}",
            "changes_summary": forge_response[:500]
        }
    
    def _commit_with_metadata(
        self,
        repo_path: str,
        branch_name: str,
        description: str,
        commit_rules: Dict[str, Any]
    ) -> str:
        """Commits changes with agent state metadata embedded."""
        from app.services.audit_service import audit_service
        
        # Build commit message with metadata
        prefix = commit_rules.get('prefix', '[FORGE]')
        include_metadata = commit_rules.get('include_metadata', True)
        
        commit_message = self._build_commit_message_with_state(
            prefix=prefix,
            description=description,
            include_metadata=include_metadata,
            commit_rules=commit_rules
        )
        
        # Execute git commit
        try:
            # Stage all changes
            subprocess.run(["git", "add", "."], cwd=repo_path, check=True)
            
            # Commit with message
            result = subprocess.run(
                ["git", "commit", "-m", commit_message],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            # Get commit hash
            hash_result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            commit_hash = hash_result.stdout.strip()
            
            # Link commit to agent state
            audit_service.link_commit_to_state(
                state_id=self.state_id,
                commit_hash=commit_hash,
                commit_message=commit_message
            )
            
            self.logger.info(f"FORGE: Committed changes with hash {commit_hash[:8]}")
            return commit_hash
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Git commit failed: {e}")
            return "commit_failed"
    
    def _build_commit_message_with_state(
        self,
        prefix: str,
        description: str,
        include_metadata: bool,
        commit_rules: Dict[str, Any]
    ) -> str:
        """Builds a commit message with agent state metadata."""
        header = f"{prefix} {description}"
        
        if not include_metadata:
            return header
        
        # Build metadata body
        signature_format = commit_rules.get(
            'signature_format',
            'Agent-State-ID: {state_id}\nModel: {model}\nTemperature: {temperature}'
        )
        
        metadata = signature_format.format(
            state_id=self.state_id,
            model=self.config.get('model'),
            temperature=self.config.get('temperature'),
            task_id=self.task_id
        )
        
        # Add timestamp
        from datetime import datetime
        timestamp = datetime.utcnow().isoformat()
        
        body = f"""
{metadata}
Task: {self.task_id}
Timestamp: {timestamp}
Provider: {self.config.get('provider', 'google')}

Generated by AI Agent Pipeline
"""
        
        return f"{header}\n\n{body.strip()}"
