"""
Celery Configuration

Configures Celery with RabbitMQ for reliable task execution.
"""

import os
from kombu import Queue

# Broker settings (RabbitMQ)
broker_url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672//")

# Result backend (database for persistence)
result_backend = os.getenv("DATABASE_URL", "sqlite:///./dev.db")
if result_backend.startswith("sqlite"):
    result_backend = f"db+{result_backend}"
elif result_backend.startswith("postgres"):
    result_backend = f"db+{result_backend}"

# Task settings for crash recovery
task_acks_late = True  # Acknowledge after task completes
task_reject_on_worker_lost = True  # Re-queue on worker crash
task_acks_on_failure_or_timeout = True

# Worker settings
worker_concurrency = int(os.getenv("MAX_WORKERS", 5))
worker_prefetch_multiplier = 1  # One task at a time per worker

# Queue definitions
task_queues = (
    Queue("default", routing_key="default"),
    Queue("pipeline", routing_key="pipeline.#"),
    Queue("release", routing_key="release.#"),
)

task_default_queue = "default"
task_default_routing_key = "default"

# Task routes
task_routes = {
    "app.tasks.run_pipeline": {"queue": "pipeline", "routing_key": "pipeline.run"},
    "app.tasks.release_task": {"queue": "release", "routing_key": "release.run"},
}

# Serialization
task_serializer = "json"
result_serializer = "json"
accept_content = ["json"]

# Task time limits
task_soft_time_limit = 3600  # 1 hour soft limit
task_time_limit = 3900  # 1 hour 5 min hard limit

# Result expiration (24 hours)
result_expires = 86400

# Timezone
timezone = "UTC"
enable_utc = True
