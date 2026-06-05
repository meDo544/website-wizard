# backend/middleware/error_handler.py

from __future__ import annotations

import traceback

from fastapi import Request
from fastapi.responses import JSONResponse

from backend.core.exceptions import (
    AppException,
)

from backend.core.logging import (
    get_logger,
)

from backend.core.logging_context import (
    get_audit_id,
    get_request_id,
    get_task_id,
)


logger = get_logger(__name__)


# ---------------------------------------------------
# Centralized Application Exception Handler
# ---------------------------------------------------

async def app_exception_handler(
    request: Request,
    exc: AppException,
):
    """
    Handle known application exceptions.

    Produces:
    - standardized API responses
    - structured logging
    - correlation-aware telemetry
    """

    request_id = get_request_id()

    audit_id = get_audit_id()

    task_id = get_task_id()

    logger.warning(

        "Application exception handled",

        request_id=request_id,

        audit_id=audit_id,

        task_id=task_id,

        method=request.method,

        path=request.url.path,

        status_code=exc.status_code,

        error_code=exc.code,

        retryable=exc.retryable,

        error_message=exc.message,
    )

    response_payload = exc.to_dict()

    # -----------------------------------------
    # Inject correlation IDs into response
    # -----------------------------------------

    response_payload["error"][
        "request_id"
    ] = request_id

    if audit_id:

        response_payload["error"][
            "audit_id"
        ] = audit_id

    if task_id:

        response_payload["error"][
            "task_id"
        ] = task_id

    return JSONResponse(

        status_code=exc.status_code,

        content=response_payload,
    )


# ---------------------------------------------------
# Generic Unhandled Exception Handler
# ---------------------------------------------------

async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
):
    """
    Handle unexpected server exceptions.

    Prevents:
    - leaking internal errors
    - inconsistent API responses
    - missing observability

    Produces:
    - standardized 500 responses
    - structured logging
    - correlation-aware telemetry
    """

    request_id = get_request_id()

    audit_id = get_audit_id()

    task_id = get_task_id()

    logger.exception(

        "Unhandled server exception",

        request_id=request_id,

        audit_id=audit_id,

        task_id=task_id,

        method=request.method,

        path=request.url.path,

        error=str(exc),
    )

    traceback.print_exc()

    response_payload = {

        "success": False,

        "error": {

            "code": (
                "internal_server_error"
            ),

            "message": (
                "An unexpected internal "
                "server error occurred."
            ),

            "request_id": request_id,
        },
    }

    if audit_id:

        response_payload["error"][
            "audit_id"
        ] = audit_id

    if task_id:

        response_payload["error"][
            "task_id"
        ] = task_id

    return JSONResponse(

        status_code=500,

        content=response_payload,
    )
