from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Routers
from backend.api.auth import router as auth_router
from backend.api.users import router as users_router
from backend.api.audit import router as audit_router

# Ensure models are registered for Alembic
from backend.models.user import User  # noqa: F401
from backend.models import audit  # noqa: F401


# ---------------------------------------------------
# App Initialization
# ---------------------------------------------------
app = FastAPI(
    title="Website Wizard API",
    version="0.1.0",
)


# ---------------------------------------------------
# CORS Middleware (🔥 FIXED + HARDENED)
# ---------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",  # 🔥 DEV MODE (allows Swagger + browser + external calls)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],  # ✅ important for auth/debug
)


# ---------------------------------------------------
# Root / Health Endpoints
# ---------------------------------------------------
@app.get("/")
def root():
    return {"message": "Website Wizard API is running 🚀"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ready")
def ready():
    return {"status": "ready"}


# ---------------------------------------------------
# API Routers
# ---------------------------------------------------
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(audit_router)