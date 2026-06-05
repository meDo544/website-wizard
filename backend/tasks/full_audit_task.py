# backend/tasks/full_audit_task.py

"""
Full audit Celery task orchestration.

This task coordinates the Website Wizard async audit lifecycle:
- Lighthouse execution
- GPT analysis
- Lifecycle stage telemetry
- Retry/failure/completion metrics
- Structured operational logs

The task intentionally keeps Prometheus labels low-cardinality. Audit IDs and
URLs are logged, but never used as metric labels.
"""

from __future__ import annotations

from typing import Any

import structlog
from celery import shared_task

from backend.core.metrics import (
    record_audit_failure,
    record_audit_retry,
    record_audit_stage,
    record_celery_retry,
    track_audit_duration,
    track_celery_task,
)
from backend.services.gpt_analyzer import analyze_with_gpt
from backend.services.lighthouse_runner import run_lighthouse_audit

logger = structlog.get_logger(__name__)

TASK_NAME = "backend.tasks.full_audit_task.run_full_audit"


def _record_stage(stage: str, *, audit_id: str) -> None:
    """Record audit stage transition with metrics and structured logs."""
    record_audit_stage(stage)
    logger.info("Audit stage transitioned", audit_id=audit_id, stage=stage)


@shared_task(
    name=TASK_NAME,
    bind=True,
    autoretry_for=(TimeoutError,),
    retry_backoff=True,
    retry_jitter=True,
    retry_kwargs={"max_retries": 3},
)
def run_full_audit(
    self,
    audit_id: str,
    url: str,
) -> dict[str, Any]:
    """
    Execute a complete Website Wizard audit.

    Args:
        audit_id: Persisted audit identifier.
        url: Target website URL.

    Returns:
        Serialized audit result payload.
    """
    task_name = self.name or TASK_NAME

    logger.info(
        "Full audit task started",
        audit_id=audit_id,
        url=url,
        task_name=task_name,
        celery_task_id=self.request.id,
        retry_count=self.request.retries,
    )

    with track_celery_task(task_name=task_name) as celery_metrics:
        with track_audit_duration() as audit_metrics:
            try:
                if self.request.retries:
                    record_audit_retry(reason="celery_retry")
                    record_celery_retry(
                        task_name=task_name,
                        reason="celery_retry",
                    )

                _record_stage("started", audit_id=audit_id)

                _record_stage("lighthouse_running", audit_id=audit_id)
                lighthouse_result = run_lighthouse_audit(url=url)

                _record_stage("gpt_analyzing", audit_id=audit_id)
                gpt_result = analyze_with_gpt(
                    audit_id=audit_id,
                    url=url,
                    lighthouse_result=lighthouse_result,
                )

                _record_stage("completed", audit_id=audit_id)

                audit_metrics["status"] = "completed"
                celery_metrics["status"] = "success"

                logger.info(
                    "Full audit task completed",
                    audit_id=audit_id,
                    url=url,
                    task_name=task_name,
                )

                return {
                    "audit_id": audit_id,
                    "url": url,
                    "status": "completed",
                    "lighthouse": lighthouse_result,
                    "analysis": gpt_result,
                }

            except TimeoutError:
                _record_stage("retrying", audit_id=audit_id)

                record_audit_retry(reason="timeout")
                record_celery_retry(task_name=task_name, reason="timeout")

                audit_metrics["status"] = "retrying"
                celery_metrics["status"] = "retrying"

                logger.exception(
                    "Full audit task timed out and may retry",
                    audit_id=audit_id,
                    url=url,
                    task_name=task_name,
                    retry_count=self.request.retries,
                )

                raise

            except Exception as exc:
                failure_type = exc.__class__.__name__

                _record_stage("failed", audit_id=audit_id)
                record_audit_failure(failure_type=failure_type)

                audit_metrics["status"] = "failed"
                celery_metrics["status"] = "failure"

                logger.exception(
                    "Full audit task failed",
                    audit_id=audit_id,
                    url=url,
                    task_name=task_name,
                    failure_type=failure_type,
                    retry_count=self.request.retries,
                )

                raise

            finally:
                logger.info(
                    "Full audit task finalized",
                    audit_id=audit_id,
                    url=url,
                    task_name=task_name,
                    celery_task_id=self.request.id,
                )
