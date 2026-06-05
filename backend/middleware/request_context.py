# backend/middleware/request_context.py

"""
Request context middleware.

Responsibilities:
- Preserve request correlation IDs.
- Bind request metadata to structlog context.
- Instrument HTTP Prometheus metrics.
- Prevent Prometheus cardinality explosion.
- Normalize FastAPI route paths safely.
- Track request latency and exceptions.

IMPORTANT:
Never use raw request.url.path directly as a Prometheus label
unless route resolution fails.
"""

from __future__ import annotations

import time
import uuid
from collections.abc import Callable

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from backend.core.metrics import (
    HTTP_EXCEPTIONS_TOTAL,
    track_request_duration,
)

logger = structlog.get_logger(__name__)

REQUEST_ID_HEADER = "X-Request-ID"
UNKNOWN_METHOD = "UNKNOWN"
UNKNOWN_ROUTE = "unmatched"


def get_normalized_route(request: Request) -> str:
    """
    Return normalized FastAPI route path.

    Examples:
        /health
        /metrics
        /audits/{audit_id}/status

    Prevents Prometheus label cardinality explosion.
    """

    route = request.scope.get("route")

    # -------------------------------------------------------------------
    # Preferred production-safe route normalization
    # -------------------------------------------------------------------

    if route and hasattr(route, "path"):
        return str(route.path)

    # -------------------------------------------------------------------
    # Fallback ONLY if route is unavailable
    # -------------------------------------------------------------------

    try:
        return request.url.path
    except Exception:
        return UNKNOWN_ROUTE


class RequestContextMiddleware(BaseHTTPMiddleware):
    """
    Production-grade request middleware.

    Features:
    - Correlation IDs
    - Structured logging
    - Request duration telemetry
    - Exception telemetry
    - Prometheus instrumentation
    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Response],
    ) -> Response:
        start_time = time.perf_counter()

        request_id = (
            request.headers.get(REQUEST_ID_HEADER)
            or str(uuid.uuid4())
        )

        method = request.method or UNKNOWN_METHOD

        # -------------------------------------------------------------------
        # Safe normalized route
        # -------------------------------------------------------------------

        route = get_normalized_route(request)

        # -------------------------------------------------------------------
        # Bind structured logging context
        # -------------------------------------------------------------------

        structlog.contextvars.clear_contextvars()

        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=method,
            route=route,
        )

        logger.info(
            "HTTP request started",
            method=method,
            route=route,
        )

        # -------------------------------------------------------------------
        # Metrics instrumentation
        # -------------------------------------------------------------------

        with track_request_duration(
            method=method,
            route=route,
        ) as metric_context:
            try:
                response = await call_next(request)

                status_code = str(response.status_code)

                metric_context["status_code"] = status_code

                response.headers[REQUEST_ID_HEADER] = request_id

                duration_seconds = round(
                    time.perf_counter() - start_time,
                    6,
                )

                logger.info(
                    "HTTP request completed",
                    method=method,
                    route=route,
                    status_code=status_code,
                    duration_seconds=duration_seconds,
                )

                return response

            except Exception as exc:
                metric_context["status_code"] = "500"

                HTTP_EXCEPTIONS_TOTAL.labels(
                    method=method,
                    route=route,
                    exception_type=exc.__class__.__name__,
                ).inc()

                duration_seconds = round(
                    time.perf_counter() - start_time,
                    6,
                )

                logger.exception(
                    "Unhandled HTTP request exception",
                    method=method,
                    route=route,
                    duration_seconds=duration_seconds,
                    exception_type=exc.__class__.__name__,
                )

                raise

            finally:
                structlog.contextvars.unbind_contextvars(
                    "request_id",
                    "method",
                    "route",
                )
