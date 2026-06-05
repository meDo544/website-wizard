from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

# Routers
from backend.api import auth
from backend.api import billing


# ---------------------------------------------------
# Environment Detection
# ---------------------------------------------------
ENV = os.getenv("ENV", "dev")  # dev | prod


# ---------------------------------------------------
# App Initialization
# ---------------------------------------------------
app = FastAPI(
    title="Website Wizard API",
    version="0.1.0",
)


# ---------------------------------------------------
# CORS Configuration
# ---------------------------------------------------
if ENV == "dev":
    origins = ["*"]
else:
    origins = [
        "https://buddiirobotics.com",
        "https://www.buddiirobotics.com",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------
# Health Endpoints
# ---------------------------------------------------
@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ready")
def ready():
    return {"status": "ready"}


@app.get("/test")
def test():
    return {"status": "ok"}


# ---------------------------------------------------
# API Routers (🔥 MUST COME BEFORE STATIC FILES)
# ---------------------------------------------------
app.include_router(auth.router)
app.include_router(billing.router)


# ---------------------------------------------------
# STATIC FILES (🔥 MUST COME LAST)
# ---------------------------------------------------
# This serves your frontend dashboard
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
