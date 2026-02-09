import logging
import os
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path
from contextvars import ContextVar

# Context variable to store task ID for traceability
task_id_ctx: ContextVar[str] = ContextVar("task_id", default="system")

class TaskFormatter(logging.Formatter):
    """Custom formatter to include task_id in logs."""
    def format(self, record):
        record.task_id = task_id_ctx.get()
        return super().format(record)

def setup_logging(log_type="api", storage_path="./storage"):
    """
    Setup structured logging with daily rotation.
    log_type: "api" or "worker"
    """
    log_dir = Path(storage_path) / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / f"{log_type}.log"
    
    # Root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Formatter
    formatter = TaskFormatter(
        '[%(asctime)s] [%(levelname)s] [%(task_id)s] [%(name)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Standard output handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Daily rotating file handler
    file_handler = TimedRotatingFileHandler(
        log_file,
        when="midnight",
        interval=1,
        backupCount=7,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    logging.info(f"Logging initialized for {log_type} (storage: {storage_path})")

def get_task_logger(task_id: str):
    """Sets the task ID in context and returns typical logger."""
    task_id_ctx.set(str(task_id))
    return logging.getLogger("task")
