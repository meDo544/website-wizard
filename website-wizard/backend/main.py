from fastapi import FastAPI

from backend.api.auth import router as auth_router
from backend.core.exception_handlers import register_exception_handlers
from backend.core.middleware import register_middleware

app = FastAPI(title="My API")

register_middleware(app)
register_exception_handlers(app)

app.include_router(auth_router)