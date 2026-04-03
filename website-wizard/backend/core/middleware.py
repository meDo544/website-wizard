import time
from uuid import uuid4

from fastapi import FastAPI, Request


def register_middleware(app: FastAPI) -> None:
    @app.middleware("http")
    async def add_request_context(request: Request, call_next):
        request.state.request_id = str(uuid4())
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = round((time.perf_counter() - start) * 1000, 2)

        response.headers["X-Request-ID"] = request.state.request_id
        response.headers["X-Process-Time-MS"] = str(duration_ms)
        return response