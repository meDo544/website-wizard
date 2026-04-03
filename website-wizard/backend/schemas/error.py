from pydantic import BaseModel


class ErrorResponse(BaseModel):
    detail: str
    code: str
    request_id: str | None = None