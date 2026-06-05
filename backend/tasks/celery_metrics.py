"""
Global Celery metrics instrumentation.

This module hooks into Celery lifecycle signals to provide:
- task execution telemetry
- duration metrics
- retry metrics
- success/failure visibility
- active task gauges

This instrumentation is intentionally centralized and reusable.

IMPORTANT:
This module must be imported once during Celery app initialization.

Example:
    import backend.tasks.celery_metrics  # noqa: F401
"""

from __future__ import annotations

import time
from typing import Dict

import structlog
from celery.signals import (
    task_failure,
    task_postrun,
    task_prerun,
    task_retry,
    task_success,
)

from backend.core.metrics import (
    CELERY_TASKS_IN_PROGRESS,
    CELERY_TASKS_TOTAL,
    CELERY_TASK_DURATION_SECONDS,
    record_celery_retry,
)

logger = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# Internal task timing registry
# ---------------------------------------------------------------------------

_task_start_times: Dict[str, float] = {}


# ---------------------------------------------------------------------------
# Signal handlers
# ---------------------------------------------------------------------------

@task_prerun.connect
def celery_task_prerun(
    task_id=None,
    task=None,
    *args,
    **kwargs,
):
    """
    Track task start time and active task gauge.
    """
    if task_id is None or task is None:
        return

    task_name = task.name or "unknown"

    _task_start_times[task_id] = time.perf_counter()

    CELERY_TASKS_IN_PROGRESS.labels(task_name=task_name).inc()

    logger.info(
        "Celery task started",
        task_id=task_id,
        task_name=task_name,
    )


@task_postrun.connect
def celery_task_postrun(
    task_id=None,
    task=None,
    state=None,
    *args,
    **kwargs,
):
    """
    Track task completion duration and decrement active gauge.
    """
    if task_id is None or task is None:
        return

    task_name = task.name or "unknown"
    status = str(state or "unknown").lower()

    start_time = _task_start_times.pop(task_id, None)

    if start_time is not None:
        duration = time.perf_counter() - start_time

        CELERY_TASK_DURATION_SECONDS.labels(
            task_name=task_name,
            status=status,
        ).observe(duration)

        logger.info(
            "Celery task duration recorded",
            task_id=task_id,
            task_name=task_name,
            status=status,
            duration_seconds=round(duration, 6),
        )

    CELERY_TASKS_IN_PROGRESS.labels(task_name=task_name).dec()

    logger.info(
        "Celery task finalized",
        task_id=task_id,
        task_name=task_name,
        status=status,
    )


@task_success.connect
def celery_task_success(
    sender=None,
    result=None,
    **kwargs,
):
    """
    Track successful task executions.
    """
    task_name = getattr(sender, "name", "unknown")

    CELERY_TASKS_TOTAL.labels(
        task_name=task_name,
        status="success",
    ).inc()

    logger.info(
        "Celery task succeeded",
        task_name=task_name,
    )


@task_failure.connect
def celery_task_failure(
    sender=None,
    task_id=None,
    exception=None,
    traceback=None,
    einfo=None,
    **kwargs,
):
    """
    Track failed task executions.
    """
    task_name = getattr(sender, "name", "unknown")

    CELERY_TASKS_TOTAL.labels(
        task_name=task_name,
        status="failure",
    ).inc()

    logger.exception(
        "Celery task failed",
        task_id=task_id,
        task_name=task_name,
        exception_type=(
            exception.__class__.__name__
            if exception
            else "unknown"
        ),
    )


@task_retry.connect
def celery_task_retry(
    request=None,
    reason=None,
    einfo=None,
    **kwargs,
):
    """
    Track Celery retry telemetry.
    """
    task_name = (
        getattr(request, "task", "unknown")
        if request
        else "unknown"
    )

    reason_label = (
        reason.__class__.__name__
        if reason
        else "unknown"
    )

    record_celery_retry(
        task_name=task_name,
        reason=reason_label,
    )

    logger.warning(
        "Celery task retry triggered",
        task_name=task_name,
        reason=reason_label,
    )
