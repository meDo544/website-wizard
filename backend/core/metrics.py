"""
Centralized Prometheus metrics registry for Website Wizard.

This module owns:
- Metric declarations
- Production-safe histogram buckets
- Reusable instrumentation context managers
- /metrics response helper

Important:
Do not create metrics dynamically outside this module. Keeping all metrics here
prevents duplicate registration, inconsistent naming, and label cardinality drift.
"""

from __future__ import annotations

import time
from contextlib import contextmanager
from typing import Generator, Optional

from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)
from starlette.responses import Response


# ---------------------------------------------------------------------------
# Histogram buckets
# ---------------------------------------------------------------------------

HTTP_LATENCY_BUCKETS = (
    0.005,
    0.01,
    0.025,
    0.05,
    0.1,
    0.25,
    0.5,
    1.0,
    2.5,
    5.0,
    10.0,
)

GPT_LATENCY_BUCKETS = (
    0.5,
    1.0,
    2.5,
    5.0,
    10.0,
    20.0,
    30.0,
    60.0,
    120.0,
    300.0,
)

LIGHTHOUSE_LATENCY_BUCKETS = (
    5.0,
    10.0,
    20.0,
    30.0,
    45.0,
    60.0,
    90.0,
    120.0,
    180.0,
    300.0,
)

AUDIT_DURATION_BUCKETS = (
    5.0,
    10.0,
    20.0,
    30.0,
    60.0,
    120.0,
    180.0,
    300.0,
    600.0,
    900.0,
)

CELERY_TASK_DURATION_BUCKETS = (
    0.1,
    0.5,
    1.0,
    2.5,
    5.0,
    10.0,
    30.0,
    60.0,
    120.0,
    300.0,
    600.0,
)


# ---------------------------------------------------------------------------
# HTTP metrics
# ---------------------------------------------------------------------------

HTTP_REQUESTS_TOTAL = Counter(
    "website_wizard_http_requests_total",
    "Total HTTP requests processed.",
    ["method", "route", "status_code"],
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "website_wizard_http_request_duration_seconds",
    "HTTP request duration in seconds.",
    ["method", "route"],
    buckets=HTTP_LATENCY_BUCKETS,
)

HTTP_REQUESTS_IN_PROGRESS = Gauge(
    "website_wizard_http_requests_in_progress",
    "Currently active HTTP requests.",
    ["method", "route"],
)

HTTP_EXCEPTIONS_TOTAL = Counter(
    "website_wizard_http_exceptions_total",
    "Total unhandled HTTP exceptions.",
    ["method", "route", "exception_type"],
)


# ---------------------------------------------------------------------------
# Audit lifecycle metrics
# ---------------------------------------------------------------------------

AUDITS_TOTAL = Counter(
    "website_wizard_audits_total",
    "Total audits processed.",
    ["status"],
)

AUDIT_DURATION_SECONDS = Histogram(
    "website_wizard_audit_duration_seconds",
    "Full audit execution duration in seconds.",
    ["status"],
    buckets=AUDIT_DURATION_BUCKETS,
)

AUDITS_IN_PROGRESS = Gauge(
    "website_wizard_audits_in_progress",
    "Currently active audits.",
)

AUDIT_STAGE_TRANSITIONS_TOTAL = Counter(
    "website_wizard_audit_stage_transitions_total",
    "Audit lifecycle stage transitions.",
    ["stage"],
)

AUDIT_FAILURES_TOTAL = Counter(
    "website_wizard_audit_failures_total",
    "Audit failures by failure type.",
    ["failure_type"],
)

AUDIT_RETRIES_TOTAL = Counter(
    "website_wizard_audit_retries_total",
    "Audit retry attempts.",
    ["reason"],
)


# ---------------------------------------------------------------------------
# GPT metrics
# ---------------------------------------------------------------------------

GPT_REQUESTS_TOTAL = Counter(
    "website_wizard_gpt_requests_total",
    "Total GPT requests.",
    ["model", "status", "user_id"],
)

GPT_REQUEST_DURATION_SECONDS = Histogram(
    "website_wizard_gpt_request_duration_seconds",
    "GPT request duration in seconds.",
    ["model", "status", "user_id"],
    buckets=GPT_LATENCY_BUCKETS,
)

GPT_REQUESTS_IN_PROGRESS = Gauge(
    "website_wizard_gpt_requests_in_progress",
    "Currently active GPT requests.",
    ["model", "user_id"],
)

GPT_TOKENS_TOTAL = Counter(
    "website_wizard_gpt_tokens_total",
    "GPT token usage.",
    ["model", "token_type", "user_id"],
)

GPT_COST_USD_TOTAL = Counter(
    "website_wizard_gpt_cost_usd_total",
    "Total GPT cost in USD.",
    ["model", "user_id"],
)


# ---------------------------------------------------------------------------
# Lighthouse metrics
# ---------------------------------------------------------------------------

LIGHTHOUSE_RUNS_TOTAL = Counter(
    "website_wizard_lighthouse_runs_total",
    "Total Lighthouse runs.",
    ["status"],
)

LIGHTHOUSE_DURATION_SECONDS = Histogram(
    "website_wizard_lighthouse_duration_seconds",
    "Lighthouse execution duration in seconds.",
    ["status"],
    buckets=LIGHTHOUSE_LATENCY_BUCKETS,
)

LIGHTHOUSE_RUNS_IN_PROGRESS = Gauge(
    "website_wizard_lighthouse_runs_in_progress",
    "Currently active Lighthouse runs.",
)


# ---------------------------------------------------------------------------
# Celery metrics
# ---------------------------------------------------------------------------

CELERY_TASKS_TOTAL = Counter(
    "website_wizard_celery_tasks_total",
    "Total Celery tasks processed.",
    ["task_name", "status"],
)

CELERY_TASK_DURATION_SECONDS = Histogram(
    "website_wizard_celery_task_duration_seconds",
    "Celery task execution duration in seconds.",
    ["task_name", "status"],
    buckets=CELERY_TASK_DURATION_BUCKETS,
)

CELERY_TASKS_IN_PROGRESS = Gauge(
    "website_wizard_celery_tasks_in_progress",
    "Currently active Celery tasks.",
    ["task_name"],
)

CELERY_TASK_RETRIES_TOTAL = Counter(
    "website_wizard_celery_task_retries_total",
    "Celery task retry attempts.",
    ["task_name", "reason"],
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def metrics_response() -> Response:
    """
    Return Prometheus scrape response.

    Intended usage:
        app.add_route("/metrics", metrics_response)
    """
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )


@contextmanager
def track_request_duration(
    *,
    method: str,
    route: str,
) -> Generator[dict[str, Optional[str]], None, None]:
    """
    Track HTTP request duration and active request gauge.

    The caller sets context["status_code"] before exit.
    """
    context: dict[str, Optional[str]] = {"status_code": None}
    start_time = time.perf_counter()

    HTTP_REQUESTS_IN_PROGRESS.labels(
        method=method,
        route=route,
    ).inc()

    try:
        yield context
    finally:
        duration = time.perf_counter() - start_time
        status_code = context.get("status_code") or "500"

        HTTP_REQUEST_DURATION_SECONDS.labels(
            method=method,
            route=route,
        ).observe(duration)

        HTTP_REQUESTS_TOTAL.labels(
            method=method,
            route=route,
            status_code=status_code,
        ).inc()

        HTTP_REQUESTS_IN_PROGRESS.labels(
            method=method,
            route=route,
        ).dec()


@contextmanager
def track_audit_duration() -> Generator[dict[str, str], None, None]:
    """
    Track full audit duration and active audit gauge.
    """
    context = {"status": "unknown"}
    start_time = time.perf_counter()

    AUDITS_IN_PROGRESS.inc()

    try:
        yield context
    finally:
        duration = time.perf_counter() - start_time
        status = context.get("status", "unknown")

        AUDIT_DURATION_SECONDS.labels(
            status=status,
        ).observe(duration)

        AUDITS_TOTAL.labels(
            status=status,
        ).inc()

        AUDITS_IN_PROGRESS.dec()


@contextmanager
def track_gpt_duration(
    *,
    model: str,
    user_id: str,
) -> Generator[dict[str, str], None, None]:
    """
    Track GPT request duration and active GPT request gauge.
    """
    context = {"status": "unknown"}
    start_time = time.perf_counter()

    GPT_REQUESTS_IN_PROGRESS.labels(
        model=model,
        user_id=user_id,
    ).inc()

    try:
        yield context
    finally:
        duration = time.perf_counter() - start_time
        status = context.get("status", "unknown")

        GPT_REQUEST_DURATION_SECONDS.labels(
            model=model,
            status=status,
            user_id=user_id,
        ).observe(duration)

        GPT_REQUESTS_TOTAL.labels(
            model=model,
            status=status,
            user_id=user_id,
        ).inc()

        GPT_REQUESTS_IN_PROGRESS.labels(
            model=model,
            user_id=user_id,
        ).dec()


@contextmanager
def track_lighthouse_duration() -> Generator[dict[str, str], None, None]:
    """
    Track Lighthouse execution duration and active run gauge.
    """
    context = {"status": "unknown"}
    start_time = time.perf_counter()

    LIGHTHOUSE_RUNS_IN_PROGRESS.inc()

    try:
        yield context
    finally:
        duration = time.perf_counter() - start_time
        status = context.get("status", "unknown")

        LIGHTHOUSE_DURATION_SECONDS.labels(
            status=status,
        ).observe(duration)

        LIGHTHOUSE_RUNS_TOTAL.labels(
            status=status,
        ).inc()

        LIGHTHOUSE_RUNS_IN_PROGRESS.dec()


@contextmanager
def track_celery_task(
    *,
    task_name: str,
) -> Generator[dict[str, str], None, None]:
    """
    Track Celery task execution duration and active task gauge.
    """
    context = {"status": "unknown"}
    start_time = time.perf_counter()

    CELERY_TASKS_IN_PROGRESS.labels(
        task_name=task_name,
    ).inc()

    try:
        yield context
    finally:
        duration = time.perf_counter() - start_time
        status = context.get("status", "unknown")

        CELERY_TASK_DURATION_SECONDS.labels(
            task_name=task_name,
            status=status,
        ).observe(duration)

        CELERY_TASKS_TOTAL.labels(
            task_name=task_name,
            status=status,
        ).inc()

        CELERY_TASKS_IN_PROGRESS.labels(
            task_name=task_name,
        ).dec()


def record_audit_stage(stage: str) -> None:
    """Record an audit lifecycle stage transition."""
    AUDIT_STAGE_TRANSITIONS_TOTAL.labels(
        stage=stage,
    ).inc()


def record_audit_failure(failure_type: str) -> None:
    """Record an audit failure by stable failure category."""
    AUDIT_FAILURES_TOTAL.labels(
        failure_type=failure_type,
    ).inc()


def record_audit_retry(reason: str) -> None:
    """Record an audit retry by stable reason label."""
    AUDIT_RETRIES_TOTAL.labels(
        reason=reason,
    ).inc()


def record_celery_retry(
    *,
    task_name: str,
    reason: str,
) -> None:
    """Record Celery retry attempts."""
    CELERY_TASK_RETRIES_TOTAL.labels(
        task_name=task_name,
        reason=reason,
    ).inc()


def record_gpt_tokens(
    *,
    model: str,
    user_id: str,
    prompt_tokens: int,
    completion_tokens: int,
    total_tokens: int,
) -> None:
    """
    Record GPT token usage.
    """

    if prompt_tokens:

        GPT_TOKENS_TOTAL.labels(
            model=model,
            token_type="prompt",
            user_id=user_id,
        ).inc(prompt_tokens)

    if completion_tokens:

        GPT_TOKENS_TOTAL.labels(
            model=model,
            token_type="completion",
            user_id=user_id,
        ).inc(completion_tokens)

    if total_tokens:

        GPT_TOKENS_TOTAL.labels(
            model=model,
            token_type="total",
            user_id=user_id,
        ).inc(total_tokens)


def record_gpt_cost(
    *,
    model: str,
    user_id: str,
    cost_usd: float,
) -> None:
    """
    Record GPT API cost usage in USD.
    """

    if cost_usd > 0:

        GPT_COST_USD_TOTAL.labels(
            model=model,
            user_id=user_id,
        ).inc(cost_usd)
