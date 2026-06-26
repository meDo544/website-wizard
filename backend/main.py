from __future__ import annotations

import os
import uuid
import backend.models
from datetime import datetime, timedelta

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from openai import OpenAI
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.core.database import SessionLocal
from backend.core.security import verify_password
from backend.core.metrics import (
    metrics_response,
    track_gpt_duration,
    record_gpt_tokens,
    record_gpt_cost,
)

from backend.core.costs import (
    calculate_gpt_cost,
)

from backend.dependencies.subscription_guard import (
    require_active_subscription,
)

from backend.middleware.request_context import RequestContextMiddleware
from backend.routes.stripe import (
    router as stripe_router,
)
from backend.routes.billing import router as billing_router
from backend.routes.websites import (
    router as websites_router,
)

import backend.models

from backend.models.generated_sites import WebsiteRecord
from backend.models.user import User

from backend.services.quota_service import check_user_quota
from backend.services.usage_service import (
    UsageService,
)

from backend.routes import auth

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GPT_MODEL_NAME = "gpt-4.1-mini"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

app = FastAPI(
    title="Website Wizard API",
    version="1.0.0",
)

app.mount(
    "/generated-sites",
    StaticFiles(directory="generated_sites"),
    name="generated-sites",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RequestContextMiddleware)

app.add_api_route(
    "/metrics",
    metrics_response,
    methods=["GET"],
)

app.include_router(stripe_router)
app.include_router(auth.router)
app.include_router(billing_router)
app.include_router(websites_router)

def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


class GenerateRequest(BaseModel):
    prompt: str


def create_access_token(data: dict) -> str:
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


@app.get("/")
def root():
    return {
        "message": "Website Wizard API running"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }

@app.get("/ready")
def ready():
    """
    Readiness probe.

    Indicates that the API process has started and is ready
    to accept requests.
    """
    return {
        "status": "ready"
    }

@app.get("/auth/history")
def get_history(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    history = (
        db.query(WebsiteRecord)
        .order_by(WebsiteRecord.created_at.desc())
        .all()
    )

    return [
        {
            "id": str(item.id),
            "prompt": item.prompt,
            "html": item.html,
            "created_at": item.created_at,
        }
        for item in history
    ]


@app.post("/auth/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.email == form_data.username)
        .first()
    )

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
        )

    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }

@app.post("/auth/generate-website")
def generate_website(
    request: GenerateRequest,

    current_user: User = Depends(
        require_active_subscription
    ),

    db: Session = Depends(get_db),
):

    user = (
        db.query(User)
        .filter(User.id == current_user.id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    user_id = str(user.id)

    user_uuid = uuid.UUID(user_id)

    # ---------------------------------------------------
    # ENFORCE QUOTAS
    # ---------------------------------------------------

    quota_ok, quota_message = check_user_quota(user)

    if not quota_ok:

        raise HTTPException(
            status_code=403,
            detail=quota_message,
        )

    # ---------------------------------------------------
    # TRACK GPT REQUEST
    # ---------------------------------------------------

    with track_gpt_duration(
        model=GPT_MODEL_NAME,
        user_id=user_id,
    ) as metric_context:

        try:

            client = OpenAI(
                api_key=OPENAI_API_KEY
            )

            response = client.chat.completions.create(
                model=GPT_MODEL_NAME,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a professional web designer. "
                            "Output ONLY clean HTML with inline CSS."
                        ),
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Create a modern website for: {request.prompt}"
                        ),
                    },
                ],
            )

            usage = response.usage

            print("GPT USAGE:", usage)

            prompt_tokens = 0
            completion_tokens = 0
            total_tokens = 0

            if usage:

                prompt_tokens = getattr(
                    usage,
                    "prompt_tokens",
                    0,
                )

                completion_tokens = getattr(
                    usage,
                    "completion_tokens",
                    0,
                )

                total_tokens = getattr(
                    usage,
                    "total_tokens",
                    0,
                )

            print(
                prompt_tokens,
                completion_tokens,
                total_tokens,
            )

            # ---------------------------------------------------
            # PROMETHEUS TOKEN METRICS
            # ---------------------------------------------------

            record_gpt_tokens(
                model=GPT_MODEL_NAME,
                user_id=user_id,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
            )

            # ---------------------------------------------------
            # GPT COST CALCULATION
            # ---------------------------------------------------

            cost_usd = calculate_gpt_cost(
                model=GPT_MODEL_NAME,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
            )

            record_gpt_cost(
                model=GPT_MODEL_NAME,
                user_id=user_id,
                cost_usd=cost_usd,
            )

            # ---------------------------------------------------
            # PERSIST USAGE TO DATABASE
            # ---------------------------------------------------

            usage_service = UsageService(db)

            usage_service.record_gpt_usage(
                user=user,
                tokens_used=total_tokens,
                estimated_cost_usd=cost_usd,
            )

            # ---------------------------------------------------
            # GENERATED HTML
            # ---------------------------------------------------

            generated_html = (
                response.choices[0]
                .message
                .content
                or ""
            )

            if generated_html.startswith("```"):

                generated_html = (
                    generated_html
                    .replace("```html", "")
                    .replace("```", "")
                )

            # ---------------------------------------------------
            # SAVE GENERATED SITE
            # ---------------------------------------------------

            new_site = WebsiteRecord(
                user_id=user_uuid,
                prompt=request.prompt,
                html=generated_html,
                gpt_model=GPT_MODEL_NAME,
                gpt_tokens_prompt=prompt_tokens,
                gpt_tokens_completion=completion_tokens,
                gpt_tokens_total=total_tokens,
                gpt_cost_usd=cost_usd,
                generation_status="completed",
            )

            db.add(user)

            db.add(new_site)

            db.commit()

            db.refresh(new_site)

            metric_context["status"] = "success"

            return {
                "id": str(new_site.id),
                "html": generated_html,
                "tokens_used": total_tokens,
                "cost_usd": round(cost_usd, 8),
                "user_id": user_id,
                "subscription_tier": user.subscription_tier,
                "monthly_tokens_used": user.monthly_tokens_used,
                "monthly_spend_used_usd": round(
                    user.monthly_spend_used_usd,
                    6,
                ),
            }

        except Exception as exc:

            import traceback

            traceback.print_exc()

            metric_context["status"] = "failure"

            raise HTTPException(
                status_code=500,
                detail=str(exc),
            )

    

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app", 
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
