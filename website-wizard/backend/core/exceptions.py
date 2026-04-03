from fastapi import status


class AppException(Exception):
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        code: str = "bad_request",
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.code = code
        super().__init__(message)


class BadRequestException(AppException):
    def __init__(self, message: str = "Bad request", code: str = "bad_request") -> None:
        super().__init__(message=message, status_code=400, code=code)


class UnauthorizedException(AppException):
    def __init__(self, message: str = "Unauthorized", code: str = "unauthorized") -> None:
        super().__init__(message=message, status_code=401, code=code)


class ForbiddenException(AppException):
    def __init__(self, message: str = "Forbidden", code: str = "forbidden") -> None:
        super().__init__(message=message, status_code=403, code=code)


class NotFoundException(AppException):
    def __init__(self, message: str = "Not found", code: str = "not_found") -> None:
        super().__init__(message=message, status_code=404, code=code)


class ConflictException(AppException):
    def __init__(self, message: str = "Conflict", code: str = "conflict") -> None:
        super().__init__(message=message, status_code=409, code=code)