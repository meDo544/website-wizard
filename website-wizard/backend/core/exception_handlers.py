import logging
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from backend.core.exceptions import AppException

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        request_id = getattr(request.state, "request_id", None)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.message,
                "code": exc.code,
                "request_id": request_id,
            },
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        request_id = getattr(request.state, "request_id", None)
        detail = exc.detail if isinstance(exc.detail, str) else "HTTP error"
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": detail,
                "code": "http_error",
                "request_id": request_id,
            },
            headers=exc.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        request_id = getattr(request.state, "request_id", None)
        return JSONResponse(
            status_code=422,
            content={
                "detail": "Validation error",
                "code": "validation_error",
                "request_id": request_id,
                "errors": exc.errors(),
            },
        )

    @app.exception_handler(IntegrityError)
    async def integrity_exception_handler(request: Request, exc: IntegrityError):
        request_id = getattr(request.state, "request_id", None)
        logger.warning("IntegrityError", exc_info=True)
        return JSONResponse(
            status_code=409,
            content={
                "detail": "Database constraint violation",
                "code": "integrity_error",
                "request_id": request_id,
            },
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
        request_id = getattr(request.state, "request_id", None)
        logger.error("SQLAlchemyError", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Database error",
                "code": "database_error",
                "request_id": request_id,
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        request_id = getattr(request.state, "request_id", None)
        logger.exception("Unhandled exception")
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "code": "internal_error",
                "request_id": request_id,
            },
        )