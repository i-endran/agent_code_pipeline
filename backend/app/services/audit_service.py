import logging
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.models import AgentExecutionLog

logger = logging.getLogger(__name__)

class AuditService:
    """Service for capturing and querying agent execution state for audit trails."""
    
    def __init__(self, storage_path: str = "./storage"):
        self.storage_path = Path(storage_path)
        self.audit_dir = self.storage_path / "audit"
        self.audit_dir.mkdir(parents=True, exist_ok=True)

    def capture_agent_state(
        self,
        agent_name: str,
        agent_config: Dict,
        task_id: str,
        user_prompt: Optional[str] = None,
        db: Optional[Session] = None
    ) -> str:
        """
        Captures a snapshot of agent configuration and returns a unique state ID.
        
        Args:
            agent_name: Name of the agent (scribe, architect, forge, etc.)
            agent_config: Full agent configuration dict
            task_id: Associated task ID
            user_prompt: Optional user-provided prompt
            db: Optional database session (creates one if not provided)
            
        Returns:
            state_id: Unique identifier for this agent execution state
        """
        state_id = str(uuid.uuid4())
        close_db = False
        
        if db is None:
            db = SessionLocal()
            close_db = True
        
        try:
            # Create execution log
            execution_log = AgentExecutionLog(
                id=state_id,
                task_id=task_id,
                agent_name=agent_name,
                model=agent_config.get("model"),
                provider=agent_config.get("provider"),
                temperature=agent_config.get("temperature"),
                max_tokens=agent_config.get("max_tokens"),
                guardrails=agent_config.get("guardrails", []),
                policies=agent_config.get("policies", {}),
                enforcement_prompt=agent_config.get("enforcement_prompt"),
                tools=agent_config.get("tools", []),
                user_prompt=user_prompt,
                started_at=datetime.utcnow(),
                status="in_progress"
            )
            
            db.add(execution_log)
            db.commit()
            
            # Save full config as JSON artifact
            artifact_path = self._save_config_artifact(state_id, agent_config, task_id)
            execution_log.config_artifact_path = artifact_path
            db.commit()
            
            logger.info(f"Captured agent state: {state_id} for {agent_name} in task {task_id}")
            return state_id
            
        except Exception as e:
            logger.error(f"Failed to capture agent state: {e}")
            db.rollback()
            raise
        finally:
            if close_db:
                db.close()

    def _save_config_artifact(self, state_id: str, config: Dict, task_id: str) -> str:
        """Saves full agent config as JSON file."""
        task_audit_dir = self.audit_dir / f"task_{task_id}"
        task_audit_dir.mkdir(parents=True, exist_ok=True)
        
        artifact_path = task_audit_dir / f"agent_state_{state_id}.json"
        
        with open(artifact_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        
        return str(artifact_path.relative_to(self.storage_path))

    def update_execution_status(
        self,
        state_id: str,
        status: str,
        error_message: Optional[str] = None,
        db: Optional[Session] = None
    ):
        """Updates the status of an agent execution."""
        close_db = False
        if db is None:
            db = SessionLocal()
            close_db = True
        
        try:
            execution_log = db.query(AgentExecutionLog).filter(
                AgentExecutionLog.id == state_id
            ).first()
            
            if execution_log:
                execution_log.status = status
                execution_log.completed_at = datetime.utcnow()
                if error_message:
                    execution_log.error_message = error_message
                db.commit()
                logger.info(f"Updated agent state {state_id} to status: {status}")
        finally:
            if close_db:
                db.close()

    def link_commit_to_state(
        self,
        state_id: str,
        commit_hash: str,
        commit_message: str,
        db: Optional[Session] = None
    ):
        """Associates a Git commit with an agent execution state."""
        close_db = False
        if db is None:
            db = SessionLocal()
            close_db = True
        
        try:
            execution_log = db.query(AgentExecutionLog).filter(
                AgentExecutionLog.id == state_id
            ).first()
            
            if execution_log:
                execution_log.commit_hash = commit_hash
                execution_log.commit_message = commit_message
                db.commit()
                logger.info(f"Linked commit {commit_hash[:8]} to agent state {state_id}")
        finally:
            if close_db:
                db.close()

    def get_state_by_id(self, state_id: str, db: Optional[Session] = None) -> Optional[AgentExecutionLog]:
        """Retrieves agent state by ID."""
        close_db = False
        if db is None:
            db = SessionLocal()
            close_db = True
        
        try:
            return db.query(AgentExecutionLog).filter(
                AgentExecutionLog.id == state_id
            ).first()
        finally:
            if close_db:
                db.close()

    def get_states_by_task(self, task_id: str, db: Optional[Session] = None) -> List[AgentExecutionLog]:
        """Lists all agent executions for a task."""
        close_db = False
        if db is None:
            db = SessionLocal()
            close_db = True
        
        try:
            return db.query(AgentExecutionLog).filter(
                AgentExecutionLog.task_id == task_id
            ).order_by(AgentExecutionLog.started_at).all()
        finally:
            if close_db:
                db.close()

    def get_state_by_commit(self, commit_hash: str, db: Optional[Session] = None) -> Optional[AgentExecutionLog]:
        """Finds agent state associated with a Git commit."""
        close_db = False
        if db is None:
            db = SessionLocal()
            close_db = True
        
        try:
            return db.query(AgentExecutionLog).filter(
                AgentExecutionLog.commit_hash == commit_hash
            ).first()
        finally:
            if close_db:
                db.close()


# Global service instance
audit_service = AuditService()
