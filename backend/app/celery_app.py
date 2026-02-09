"""
Celery Application

Creates the Celery app instance for background task processing.
"""

from celery import Celery

# Create Celery app
celery_app = Celery("sdlc_agents")

# Load configuration
celery_app.config_from_object("celeryconfig")

# Auto-discover tasks
celery_app.autodiscover_tasks(["app.tasks"])

# Initialize worker logging
from app.services.logging_service import setup_logging
setup_logging(log_type="worker")


if __name__ == "__main__":
    celery_app.start()
