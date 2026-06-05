"""
Canonical Celery Application
Used by:
- backend
- celery worker
- flower
- async website generation
"""

from celery import Celery
from celery.schedules import crontab
import os

# -------------------------------------------------------------------
# Environment Configuration
# -------------------------------------------------------------------

CELERY_BROKER_URL = os.getenv(
    "CELERY_BROKER_URL",
    "redis://redis:6379/0",
)

CELERY_RESULT_BACKEND = os.getenv(
    "CELERY_RESULT_BACKEND",
    "redis://redis:6379/0",
)

# -------------------------------------------------------------------
# Celery Application
# -------------------------------------------------------------------

celery_app = Celery(
    "website_wizard",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
)

# -------------------------------------------------------------------
# Celery Configuration
# -------------------------------------------------------------------

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    result_expires=3600,
    broker_connection_retry_on_startup=True,
)

# -------------------------------------------------------------------
# Celery Beat Schedule
# -------------------------------------------------------------------

celery_app.conf.beat_schedule = {
    "reset-monthly-ai-quotas": {
        "task": (
            "backend.tasks.quota_reset."
            "reset_monthly_quotas_task"
        ),
        "schedule": crontab(
            day_of_month=1,
            hour=0,
            minute=0,
        ),
    },
}

# -------------------------------------------------------------------
# Auto Discover Tasks
# -------------------------------------------------------------------

celery_app.autodiscover_tasks(
    [
        "backend.tasks",
    ]
)

# -------------------------------------------------------------------
# Explicit Critical Imports
# -------------------------------------------------------------------

import backend.tasks.website_generation
