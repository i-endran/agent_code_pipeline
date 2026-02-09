"""
Celery Tasks

Background tasks for pipeline execution.
"""

from datetime import datetime
from celery import shared_task

from app.celery_app import celery_app
from app.db.database import SessionLocal
from app.models.models import Task, TaskStatus, AgentStage, StageLog


@celery_app.task(bind=True, name="app.tasks.run_pipeline")
def run_pipeline(self, task_id: int):
    """
    Execute a pipeline task through all enabled agents.
    
    This is the main entry point for pipeline execution.
    """
    db = SessionLocal()
    
    try:
        # Get task
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        # Update status
        task.status = TaskStatus.PROCESSING
        task.started_at = datetime.utcnow()
        db.commit()
        
        # Get enabled agents from pipeline
        pipeline = task.pipeline
        enabled_agents = pipeline.enabled_agents
        
        # Execute each agent in sequence
        agent_stages = {
            "scribe": AgentStage.SCRIBE,
            "architect": AgentStage.ARCHITECT,
            "forge": AgentStage.FORGE,
            "herald": AgentStage.HERALD,
            "sentinel": AgentStage.SENTINEL,
            "phoenix": AgentStage.PHOENIX,
        }
        
        current_context = task.context.copy()
        artifacts = {}
        total_tokens = 0
        total_cost = 0.0
        
        for agent_id in enabled_agents:
            stage = agent_stages.get(agent_id)
            if not stage:
                continue
            
            # Update current stage
            task.current_stage = stage
            db.commit()
            
            # Create stage log
            stage_log = StageLog(
                task_id=task_id,
                stage=stage,
                status="started",
                started_at=datetime.utcnow(),
                input_data=current_context
            )
            db.add(stage_log)
            db.commit()
            
            try:
                # TODO: Actually execute the agent
                # result = execute_agent(agent_id, current_context)
                
                # Placeholder for now
                result = {
                    "output": f"Output from {agent_id}",
                    "tokens_used": 100,
                    "cost": 0.01
                }
                
                # Update stage log
                stage_log.status = "completed"
                stage_log.completed_at = datetime.utcnow()
                stage_log.duration_seconds = (
                    stage_log.completed_at - stage_log.started_at
                ).total_seconds()
                stage_log.output_data = result
                stage_log.input_tokens = result.get("tokens_used", 0) // 2
                stage_log.output_tokens = result.get("tokens_used", 0) // 2
                
                # Accumulate results
                artifacts[agent_id] = result.get("output")
                total_tokens += result.get("tokens_used", 0)
                total_cost += result.get("cost", 0.0)
                
                # Update context for next agent
                current_context[f"{agent_id}_output"] = result.get("output")
                
            except Exception as e:
                stage_log.status = "failed"
                stage_log.error_message = str(e)
                stage_log.completed_at = datetime.utcnow()
                
                task.status = TaskStatus.FAILED
                task.error_message = f"Failed at {agent_id}: {str(e)}"
                db.commit()
                raise
            
            db.commit()
        
        # Complete task
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.utcnow()
        task.artifacts = artifacts
        task.actual_tokens = total_tokens
        task.actual_cost = total_cost
        task.token_usage = {
            "total": total_tokens,
            "by_agent": {
                a: artifacts.get(a, {}) for a in enabled_agents
            }
        }
        db.commit()
        
        return {"task_id": task_id, "status": "completed"}
        
    except Exception as e:
        # Mark as failed
        task = db.query(Task).filter(Task.id == task_id).first()
        if task:
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            task.completed_at = datetime.utcnow()
            db.commit()
        raise
        
    finally:
        db.close()


@celery_app.task(bind=True, name="app.tasks.release_task")
def release_task(self, task_id: int):
    """
    Process a task in the release queue.
    
    Called when the releaser agent is activated.
    """
    # TODO: Implement release processing
    pass
