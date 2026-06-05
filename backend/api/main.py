# backend/api/main.py

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import (
    CORSMiddleware,
)

# ---------------------------------------------------
# Logging
# ---------------------------------------------------

from backend.core.logging import (
    configure_logging,
    get_logger,
)

# ---------------------------------------------------
# Metrics
# ---------------------------------------------------

from backend.core.metrics import (
    metrics_response,
)

# ---------------------------------------------------
# Startup Validation
# ---------------------------------------------------

from backend.core.startup import (
    run_startup_checks,
)

# ---------------------------------------------------
# Middleware
# ---------------------------------------------------

from backend.middleware.request_context import (
    RequestContextMiddleware,
)

# ---------------------------------------------------
# Exception Handlers
# ---------------------------------------------------

from backend.core.exceptions import (
    AppException,
)

from backend.middleware.error_handler import (
    app_exception_handler,
    unhandled_exception_handler,
)

# ---------------------------------------------------
# API Routers
# ---------------------------------------------------

# Authentication
from backend.api.auth import (
    router as auth_router,
)

# Website management
from backend.routes.sites import (
    router as sites_router,
)

# Billing / subscriptions
from backend.routes.billing import (
    router as billing_router,
)

# Admin analytics
from backend.routes.admin_analytics import (
    router as admin_analytics_router,
)

# Website audits + SSE streaming
from backend.routes.audits import (
    router as audits_router,
)

# ---------------------------------------------------
# Configure Logging
# ---------------------------------------------------

configure_logging()

logger = get_logger(__name__)

# ---------------------------------------------------
# FastAPI Application
# ---------------------------------------------------

app = FastAPI(

    title="Website Wizard API",

    description=(
        "Production-grade async SaaS backend "
        "for Website Wizard"
    ),

    version="1.0.0",
)

# ---------------------------------------------------
# Middleware Registration
# ---------------------------------------------------

app.add_middleware(
    RequestContextMiddleware
)

app.add_middleware(

    CORSMiddleware,

    # -------------------------------------------------
    # IMPORTANT:
    #
    # Restrict origins in production.
    # Example:
    #
    # allow_origins=[
    #     "https://app.websitewizard.com",
    # ]
    # -------------------------------------------------

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)

# ---------------------------------------------------
# Exception Handlers
# ---------------------------------------------------

app.add_exception_handler(

    AppException,

    app_exception_handler,
)

app.add_exception_handler(

    Exception,

    unhandled_exception_handler,
)

# ---------------------------------------------------
# Startup Events
# ---------------------------------------------------

@app.on_event("startup")
def startup_event():
    """
    Execute application startup validation.

    Includes:
    - environment validation
    - role validation
    - plan validation
    - infrastructure validation
    """

    logger.info(
        "Starting Website Wizard API"
    )

    run_startup_checks()

    logger.info(
        "Startup validation completed successfully"
    )

# ---------------------------------------------------
# Shutdown Events
# ---------------------------------------------------

@app.on_event("shutdown")
def shutdown_event():
    """
    Graceful application shutdown.
    """

    logger.info(
        "Shutting down Website Wizard API"
    )

# ---------------------------------------------------
# Root Endpoints
# ---------------------------------------------------

@app.get("/")
def root():
    """
    Root API endpoint.
    """

    logger.info(
        "Root endpoint accessed"
    )

    return {

        "message": (
            "Website Wizard API is running 🚀"
        ),
    }


@app.get("/health")
def health():
    """
    Health check endpoint.

    Useful for:
    - load balancers
    - Docker health checks
    - uptime monitoring
    - orchestration systems
    """

    logger.info(
        "Health check endpoint accessed"
    )

    return {
        "status": "ok"
    }

# ---------------------------------------------------
# Metrics Endpoint
# ---------------------------------------------------

@app.get("/metrics")
def metrics():
    """
    Prometheus metrics endpoint.
    """

    logger.info(
        "Metrics endpoint accessed"
    )

    return metrics_response()

# ---------------------------------------------------
# Router Registration
# ---------------------------------------------------

# Authentication
app.include_router(auth_router)

# Website management
app.include_router(sites_router)

# Billing / subscriptions / usage
app.include_router(billing_router)

# Admin analytics
app.include_router(
    admin_analytics_router
)

# Async audits + SSE streaming
app.include_router(audits_router)

# ---------------------------------------------------
# Startup Completion Log
# ---------------------------------------------------

logger.info(
    "All API routers registered successfully"
)
