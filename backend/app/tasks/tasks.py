import logging
import asyncio
from datetime import datetime
from sqlalchemy.orm import Session
from app.celery_app import celery_app
from app.db.database import SessionLocal
from app.models.models import Task, TaskStatus, AgentStage, StageLog, Repository
from app.models.approval import ApprovalCheckpoint
from app.services.repo_service import repo_service
from app.services.artifact_service import artifact_service
from app.services.approval_service import approval_service
from app.utils.task_utils import send_task_update

logger = logging.getLogger(__name__)

async def execute_pipeline(task_id: str):
    """Internal async function to run the pipeline logic."""
    db: Session = SessionLocal()
    task = db.query(Task).filter(Task.id == task_id).first()
    
    if not task:
        logger.error(f"Task {task_id} not found")
        return
    
    try:
        task.status = TaskStatus.PROCESSING
        task.started_at = datetime.utcnow()
        db.commit()
        
        # Initial status update
        send_task_update(task_id, {
            "status": "processing",
            "progress": 5,
            "message": "Starting pipeline execution..."
        })
        
        # Context for agents
        context = task.config.copy()
        context["task_id"] = task_id
        context["storage_path"] = "./storage"
        
        # 1. Initialize Repository
        repo_url = context.get("scribe", {}).get("project_context", "")
        if "http" in repo_url:
            send_task_update(task_id, {"message": "Initializing repository..."})
            
            repo = db.query(Repository).filter(Repository.source_url == repo_url).first()
            if not repo:
                repo = Repository(source_url=repo_url, local_path=f"./storage/repos/repo_{task_id}")
                db.add(repo)
                db.commit()
            
            task.repository_id = repo.id
            db.commit()
            
            # Clone repo
            repo_path = repo_service.clone_repo(task_id, repo_url)
            repo.local_path = repo_path
            repo.clone_status = "cloned"
            db.commit()
            
            context["repo_path"] = repo_path
            send_task_update(task_id, {"message": f"Repository cloned to {repo_path}"})

        # 2. SCRIBE Stage
        from app.agents.scribe_agent import ScribeAgent
        send_task_update(task_id, {"current_stage": "scribe", "progress": 20, "message": "Executing SCRIBE..."})
        scribe = ScribeAgent(context["scribe"], task_id)
        scribe_results = await scribe.run(context)
        context["scribe_results"] = scribe_results
        send_task_update(task_id, {"current_stage": "scribe", "status": "completed", "progress": 35, "message": "SCRIBE completed"})
        
        # HITL Checkpoint: SCRIBE Output
        if context.get("scribe", {}).get("approval_required"):
            approval_service.create_approval_request(
                db=db,
                task_id=task_id,
                checkpoint=ApprovalCheckpoint.SCRIBE_OUTPUT,
                agent_name="scribe",
                artifact_paths=scribe_results.get("artifact_paths", []),
                summary=scribe_results.get("summary", "SCRIBE output ready for review"),
                details=scribe_results,
                timeout_minutes=context["scribe"].get("approval_timeout_minutes", 60),
                auto_approve_on_timeout=False
            )
            return  # Pause execution, will resume after approval

        # 3. ARCHITECT Stage
        if context.get("architect", {}).get("enabled"):
            from app.agents.architect_agent import ArchitectAgent
            send_task_update(task_id, {"current_stage": "architect", "progress": 40, "message": "Executing ARCHITECT..."})
            architect = ArchitectAgent(context["architect"], task_id)
            architect_results = await architect.run(context)
            context["architect_results"] = architect_results
            send_task_update(task_id, {"current_stage": "architect", "status": "completed", "progress": 55, "message": "ARCHITECT completed"})
            
            # HITL Checkpoint: ARCHITECT Plan
            if context.get("architect", {}).get("approval_required"):
                approval_service.create_approval_request(
                    db=db,
                    task_id=task_id,
                    checkpoint=ApprovalCheckpoint.ARCHITECT_PLAN,
                    agent_name="architect",
                    artifact_paths=architect_results.get("artifact_paths", []),
                    summary=architect_results.get("summary", "Technical plan ready for review"),
                    details=architect_results,
                    timeout_minutes=context["architect"].get("approval_timeout_minutes", 60),
                    auto_approve_on_timeout=False
                )
                return  # Pause execution

        # 4. FORGE Stage
        if context.get("forge", {}).get("enabled"):
            from app.agents.forge_agent import ForgeAgent
            send_task_update(task_id, {"current_stage": "forge", "progress": 60, "message": "Executing FORGE..."})
            forge = ForgeAgent(context["forge"], task_id)
            forge_results = await forge.run(context)
            context["forge_results"] = forge_results
            send_task_update(task_id, {"current_stage": "forge", "status": "completed", "progress": 75, "message": "FORGE completed"})
            
            # HITL Checkpoint: FORGE Code
            if context.get("forge", {}).get("approval_required"):
                approval_service.create_approval_request(
                    db=db,
                    task_id=task_id,
                    checkpoint=ApprovalCheckpoint.FORGE_CODE,
                    agent_name="forge",
                    artifact_paths=forge_results.get("artifact_paths", []),
                    summary=forge_results.get("summary", "Code changes ready for review"),
                    details=forge_results,
                    timeout_minutes=context["forge"].get("approval_timeout_minutes", 60),
                    auto_approve_on_timeout=False
                )
                return  # Pause execution

        # 5. SENTINEL Stage
        if context.get("sentinel", {}).get("enabled"):
            from app.agents.sentinel_agent import SentinelAgent
            send_task_update(task_id, {"current_stage": "sentinel", "progress": 80, "message": "Executing SENTINEL..."})
            sentinel = SentinelAgent(context["sentinel"], task_id)
            sentinel_results = await sentinel.run(context)
            context["sentinel_results"] = sentinel_results
            send_task_update(task_id, {"current_stage": "sentinel", "status": "completed", "progress": 95, "message": "SENTINEL completed"})
            
            # HITL Checkpoint: SENTINEL Review
            if context.get("sentinel", {}).get("approval_required"):
                approval_service.create_approval_request(
                    db=db,
                    task_id=task_id,
                    checkpoint=ApprovalCheckpoint.SENTINEL_REVIEW,
                    agent_name="sentinel",
                    artifact_paths=sentinel_results.get("artifact_paths", []),
                    summary=sentinel_results.get("summary", "Code review ready for approval"),
                    details=sentinel_results,
                    timeout_minutes=context["sentinel"].get("approval_timeout_minutes", 60),
                    auto_approve_on_timeout=False
                )
                return  # Pause execution
            
            if sentinel_results.get("action") == "reworking":
                send_task_update(task_id, {"message": "Fixes required. Routing back to FORGE (simulation)..."})

        # 6. PHOENIX Stage
        if context.get("phoenix", {}).get("enabled"):
            from app.agents.phoenix_agent import PhoenixAgent
            send_task_update(task_id, {"current_stage": "phoenix", "progress": 96, "message": "Executing PHOENIX (Release)..."})
            phoenix = PhoenixAgent(context["phoenix"], task_id)
            phoenix_results = await phoenix.run(context)
            context["phoenix_results"] = phoenix_results
            
            # HITL Checkpoint: PHOENIX Release
            if context.get("phoenix", {}).get("approval_required"):
                approval_service.create_approval_request(
                    db=db,
                    task_id=task_id,
                    checkpoint=ApprovalCheckpoint.PHOENIX_RELEASE,
                    agent_name="phoenix",
                    artifact_paths=phoenix_results.get("artifact_paths", []),
                    summary=phoenix_results.get("summary", "Release ready for approval"),
                    details=phoenix_results,
                    timeout_minutes=context["phoenix"].get("approval_timeout_minutes", 60),
                    auto_approve_on_timeout=False
                )
                return  # Pause execution
            
            if phoenix_results.get("status") == "waiting":
                task.status = TaskStatus.AWAITING_REVIEW # Use this for MR pending too
                db.commit()
                send_task_update(task_id, {
                    "current_stage": "phoenix", 
                    "status": "waiting", 
                    "progress": 95, 
                    "message": phoenix_results.get("message")
                })
                return # Pause execution

            send_task_update(task_id, {"current_stage": "phoenix", "status": "completed", "progress": 100, "message": "PHOENIX completed"})

        # Finalize
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.utcnow()
        db.commit()
        
        send_task_update(task_id, {
            "status": "completed",
            "progress": 100,
            "message": "Pipeline completed successfully!"
        })

    except Exception as e:
        logger.error(f"Pipeline failed for task {task_id}: {e}", exc_info=True)
        task.status = TaskStatus.FAILED
        task.error_message = str(e)
        db.commit()
        send_task_update(task_id, {
            "status": "failed",
            "message": f"Pipeline failed: {str(e)}"
        })
    finally:
        db.close()

@celery_app.task(name="app.tasks.run_pipeline")
def run_pipeline(task_id: str):
    """Celery task wrapper for pipeline execution."""
    asyncio.run(execute_pipeline(task_id))

@celery_app.task(name="app.tasks.periodic_cleanup")
def periodic_cleanup(max_age_days: int = 7):
    """Celery task for periodic storage cleanup."""
    from app.services.cleanup_service import cleanup_service
    cleanup_service.run_cleanup(max_age_days=max_age_days)


@celery_app.task(name="app.tasks.resume_pipeline")
def resume_pipeline(task_id: str, checkpoint: str):
    """
    Resume pipeline execution after approval.
    
    Args:
        task_id: Task ID to resume
        checkpoint: Checkpoint where execution was paused
    """
    logger.info(f"Resuming pipeline for task {task_id} from checkpoint {checkpoint}")
    # Re-run the main pipeline, it will skip to the next stage
    asyncio.run(execute_pipeline(task_id))


@celery_app.task(name="app.tasks.rerun_agent")
def rerun_agent(task_id: str, checkpoint: str, feedback: dict = None):
    """
    Re-run a specific agent after rejection.
    
    Args:
        task_id: Task ID
        checkpoint: Checkpoint that was rejected
        feedback: Feedback from rejection
    """
    logger.info(f"Re-running agent for task {task_id} at checkpoint {checkpoint} with feedback")
    # For now, just re-run the entire pipeline
    # In production, this would intelligently restart from the specific agent
    asyncio.run(execute_pipeline(task_id))


@celery_app.task(name="app.tasks.check_approval_timeouts")
def check_approval_timeouts():
    """Periodic task to check for approval timeouts."""
    db = SessionLocal()
    try:
        timed_out = approval_service.check_timeouts(db)
        logger.info(f"Checked approval timeouts: {len(timed_out)} timed out")
    finally:
        db.close()
