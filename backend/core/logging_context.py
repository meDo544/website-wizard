# backend/core/logging_context.py

from __future__ import annotations

from contextvars import ContextVar
from typing import Optional


# ---------------------------------------------------
# Context Variables
# ---------------------------------------------------

request_id_context: ContextVar[
    Optional[str]
] = ContextVar(
    "request_id",
    default=None,
)

audit_id_context: ContextVar[
    Optional[str]
] = ContextVar(
    "audit_id",
    default=None,
)

task_id_context: ContextVar[
    Optional[str]
] = ContextVar(
    "task_id",
    default=None,
)


# ---------------------------------------------------
# Request ID Helpers
# ---------------------------------------------------

def set_request_id(
    request_id: str,
) -> None:
    """
    Store current request ID in context.
    """

    request_id_context.set(
        request_id
    )


def get_request_id() -> Optional[str]:
    """
    Retrieve current request ID.
    """

    return request_id_context.get()


def clear_request_id() -> None:
    """
    Clear request ID context.
    """

    request_id_context.set(None)


# ---------------------------------------------------
# Audit ID Helpers
# ---------------------------------------------------

def set_audit_id(
    audit_id: str,
) -> None:
    """
    Store current audit ID in context.
    """

    audit_id_context.set(
        audit_id
    )


def get_audit_id() -> Optional[str]:
    """
    Retrieve current audit ID.
    """

    return audit_id_context.get()


def clear_audit_id() -> None:
    """
    Clear audit ID context.
    """

    audit_id_context.set(None)


# ---------------------------------------------------
# Celery Task ID Helpers
# ---------------------------------------------------

def set_task_id(
    task_id: str,
) -> None:
    """
    Store current Celery task ID.
    """

    task_id_context.set(
        task_id
    )


def get_task_id() -> Optional[str]:
    """
    Retrieve current Celery task ID.
    """

    return task_id_context.get()


def clear_task_id() -> None:
    """
    Clear Celery task ID context.
    """

    task_id_context.set(None)


# ---------------------------------------------------
# Clear All Context
# ---------------------------------------------------

def clear_logging_context() -> None:
    """
    Clear all request-scoped logging context.

    Useful for:
    - request cleanup
    - Celery cleanup
    - worker reuse safety
    """

    clear_request_id()

    clear_audit_id()

    clear_task_id()
