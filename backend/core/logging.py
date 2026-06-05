# backend/core/logging.py

from __future__ import annotations

import logging
import sys

from typing import Any

import structlog

from backend.core.logging_context import (
    get_audit_id,
    get_request_id,
    get_task_id,
)


# ---------------------------------------------------
# Context Injection Processor
# ---------------------------------------------------

def add_correlation_context(
    logger: Any,
    method_name: str,
    event_dict: dict,
) -> dict:
    """
    Inject correlation IDs into all logs.

    Automatically attaches:
    - request_id
    - audit_id
    - task_id

    This enables:
    - distributed tracing
    - async debugging
    - Celery observability
    - audit lifecycle tracing
    """

    request_id = get_request_id()

    audit_id = get_audit_id()

    task_id = get_task_id()

    if request_id:

        event_dict["request_id"] = (
            request_id
        )

    if audit_id:

        event_dict["audit_id"] = (
            audit_id
        )

    if task_id:

        event_dict["task_id"] = (
            task_id
        )

    return event_dict


# ---------------------------------------------------
# Logging Configuration
# ---------------------------------------------------

def configure_logging() -> None:
    """
    Configure centralized structured logging.

    Goals:
    - JSON structured logs
    - production observability
    - Celery compatibility
    - FastAPI compatibility
    - scalable log aggregation
    - distributed request tracing
    """

    shared_processors = [

        # -----------------------------------------
        # Correlation context
        # -----------------------------------------

        add_correlation_context,

        # -----------------------------------------
        # Add log level
        # -----------------------------------------

        structlog.processors.add_log_level,

        # -----------------------------------------
        # Add timestamp
        # -----------------------------------------

        structlog.processors.TimeStamper(
            fmt="iso",
        ),

        # -----------------------------------------
        # Stack traces
        # -----------------------------------------

        structlog.processors.StackInfoRenderer(),

        # -----------------------------------------
        # Exception formatting
        # -----------------------------------------

        structlog.processors.format_exc_info,

        # -----------------------------------------
        # Unicode safety
        # -----------------------------------------

        structlog.processors.UnicodeDecoder(),
    ]

    # -------------------------------------------------
    # Standard Library Logging
    # -------------------------------------------------

    logging.basicConfig(

        format="%(message)s",

        stream=sys.stdout,

        level=logging.INFO,
    )

    # -------------------------------------------------
    # Reduce noisy third-party logs
    # -------------------------------------------------

    logging.getLogger(
        "uvicorn.access"
    ).setLevel(logging.WARNING)

    logging.getLogger(
        "urllib3"
    ).setLevel(logging.WARNING)

    logging.getLogger(
        "httpx"
    ).setLevel(logging.WARNING)

    # -------------------------------------------------
    # Structlog Configuration
    # -------------------------------------------------

    structlog.configure(

        processors=[

            *shared_processors,

            # ---------------------------------
            # Render final JSON log output
            # ---------------------------------

            structlog.processors.JSONRenderer(),
        ],

        wrapper_class=(
            structlog.make_filtering_bound_logger(
                logging.INFO
            )
        ),

        logger_factory=(
            structlog.stdlib.LoggerFactory()
        ),

        cache_logger_on_first_use=True,
    )


# ---------------------------------------------------
# Logger Retrieval
# ---------------------------------------------------

def get_logger(name: str):
    """
    Retrieve structured logger instance.

    Usage:
        logger = get_logger(__name__)
    """

    return structlog.get_logger(name)
