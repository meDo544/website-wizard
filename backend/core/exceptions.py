# backend/core/exceptions.py

from __future__ import annotations

from typing import Any
from typing import Dict
from typing import Optional

from fastapi import status


# ---------------------------------------------------
# Base Application Exception
# ---------------------------------------------------

class AppException(Exception):
    """
    Base application exception.

    Standardized exception format for:
    - API responses
    - worker failures
    - infrastructure errors
    - business logic errors
    """

    def __init__(
        self,
        message: str,
        status_code: int = (
            status.HTTP_400_BAD_REQUEST
        ),
        code: str = "bad_request",
        details: Optional[
            Dict[str, Any]
        ] = None,
        retryable: bool = False,
    ) -> None:

        self.message = message

        self.status_code = status_code

        self.code = code

        self.details = details or {}

        self.retryable = retryable

        super().__init__(message)

    def to_dict(self) -> dict:
        """
        Convert exception into API-safe payload.
        """

        return {

            "success": False,

            "error": {

                "code": self.code,

                "message": self.message,

                "details": self.details,

                "retryable": (
                    self.retryable
                ),
            },
        }


# ---------------------------------------------------
# Generic HTTP Exceptions
# ---------------------------------------------------

class BadRequestException(
    AppException
):
    def __init__(
        self,
        message: str = "Bad request",
        code: str = "bad_request",
        details: Optional[
            Dict[str, Any]
        ] = None,
    ) -> None:

        super().__init__(

            message=message,

            status_code=(
                status.HTTP_400_BAD_REQUEST
            ),

            code=code,

            details=details,
        )


class UnauthorizedException(
    AppException
):
    def __init__(
        self,
        message: str = "Unauthorized",
        code: str = "unauthorized",
        details: Optional[
            Dict[str, Any]
        ] = None,
    ) -> None:

        super().__init__(

            message=message,

            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),

            code=code,

            details=details,
        )


class ForbiddenException(
    AppException
):
    def __init__(
        self,
        message: str = "Forbidden",
        code: str = "forbidden",
        details: Optional[
            Dict[str, Any]
        ] = None,
    ) -> None:

        super().__init__(

            message=message,

            status_code=(
                status.HTTP_403_FORBIDDEN
            ),

            code=code,

            details=details,
        )


class NotFoundException(
    AppException
):
    def __init__(
        self,
        message: str = "Not found",
        code: str = "not_found",
        details: Optional[
            Dict[str, Any]
        ] = None,
    ) -> None:

        super().__init__(

            message=message,

            status_code=(
                status.HTTP_404_NOT_FOUND
            ),

            code=code,

            details=details,
        )


class ConflictException(
    AppException
):
    def __init__(
        self,
        message: str = "Conflict",
        code: str = "conflict",
        details: Optional[
            Dict[str, Any]
        ] = None,
    ) -> None:

        super().__init__(

            message=message,

            status_code=(
                status.HTTP_409_CONFLICT
            ),

            code=code,

            details=details,
        )


# ---------------------------------------------------
# Validation Exceptions
# ---------------------------------------------------

class ValidationException(
    AppException
):
    def __init__(
        self,
        message: str = (
            "Validation failed"
        ),
        details: Optional[
            Dict[str, Any]
        ] = None,
    ) -> None:

        super().__init__(

            message=message,

            status_code=(
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ),

            code="validation_error",

            details=details,
        )


# ---------------------------------------------------
# Infrastructure Exceptions
# ---------------------------------------------------

class ExternalServiceException(
    AppException
):
    """
    External dependency failure.

    Examples:
    - OpenAI
    - Lighthouse
    - Stripe
    - external APIs
    """

    def __init__(
        self,
        message: str = (
            "External service failure"
        ),
        code: str = (
            "external_service_error"
        ),
        details: Optional[
            Dict[str, Any]
        ] = None,
        retryable: bool = True,
    ) -> None:

        super().__init__(

            message=message,

            status_code=(
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),

            code=code,

            details=details,

            retryable=retryable,
        )


class DatabaseException(
    AppException
):
    def __init__(
        self,
        message: str = (
            "Database operation failed"
        ),
        details: Optional[
            Dict[str, Any]
        ] = None,
        retryable: bool = True,
    ) -> None:

        super().__init__(

            message=message,

            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),

            code="database_error",

            details=details,

            retryable=retryable,
        )


class RateLimitException(
    AppException
):
    def __init__(
        self,
        message: str = (
            "Rate limit exceeded"
        ),
        details: Optional[
            Dict[str, Any]
        ] = None,
    ) -> None:

        super().__init__(

            message=message,

            status_code=(
                status.HTTP_429_TOO_MANY_REQUESTS
            ),

            code="rate_limit_exceeded",

            details=details,
        )


# ---------------------------------------------------
# Audit Pipeline Exceptions
# ---------------------------------------------------

class AuditException(
    AppException
):
    """
    Base audit pipeline exception.
    """

    def __init__(
        self,
        message: str = (
            "Audit processing failed"
        ),
        code: str = "audit_error",
        details: Optional[
            Dict[str, Any]
        ] = None,
        retryable: bool = False,
    ) -> None:

        super().__init__(

            message=message,

            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),

            code=code,

            details=details,

            retryable=retryable,
        )


class LighthouseException(
    AuditException
):
    def __init__(
        self,
        message: str = (
            "Lighthouse audit failed"
        ),
        details: Optional[
            Dict[str, Any]
        ] = None,
        retryable: bool = True,
    ) -> None:

        super().__init__(

            message=message,

            code="lighthouse_error",

            details=details,

            retryable=retryable,
        )


class GPTAnalysisException(
    AuditException
):
    def __init__(
        self,
        message: str = (
            "GPT analysis failed"
        ),
        details: Optional[
            Dict[str, Any]
        ] = None,
        retryable: bool = True,
    ) -> None:

        super().__init__(

            message=message,

            code="gpt_analysis_error",

            details=details,

            retryable=retryable,
        )


class CrawlException(
    AuditException
):
    def __init__(
        self,
        message: str = (
            "Website crawl failed"
        ),
        details: Optional[
            Dict[str, Any]
        ] = None,
        retryable: bool = True,
    ) -> None:

        super().__init__(

            message=message,

            code="crawl_error",

            details=details,

            retryable=retryable,
        )
