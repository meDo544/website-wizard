from fastapi import APIRouter, Depends, Request, status, HTTPException, Response, Query
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel
import os

from jose import jwt, JWTError

from backend.core.dependencies import get_db
from backend.models.user import User
from backend.models.generated_site import GeneratedSite
from backend.schemas.auth import (
    RefreshTokenRequest,
    TokenPair,
    UserOut,
    UserRegister,
)
from backend.services.auth_service import AuthService
from backend.core.security import SECRET_KEY, ALGORITHM

from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# =========================
# AUTH ROUTES
# =========================

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    return AuthService(db).register_user(payload.email, payload.password)


@router.post("/login", response_model=TokenPair)
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    service = AuthService(db)

    user = service.authenticate_user(
        email=form_data.username,
        password=form_data.password,
    )

    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return service.issue_token_pair(
        user,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
    )


@router.post("/refresh", response_model=TokenPair)
def refresh(payload: RefreshTokenRequest, db: Session = Depends(get_db)):
    return AuthService(db).refresh_access_token(payload.refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(payload: RefreshTokenRequest, db: Session = Depends(get_db)):
    AuthService(db).revoke_refresh_token(payload.refresh_token)
    return None


# =========================
# CURRENT USER
# =========================

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")

        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")

        user = db.query(User).filter(User.email == email).first()

        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        return user

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.get("/me")
def read_me(current_user: User = Depends(get_current_user)):
    return {
        "id": str(current_user.id),
        "email": current_user.email,
    }


# =========================
# WEBSITE GENERATOR
# =========================

class GenerateRequest(BaseModel):
    prompt: str


def clean_generated_html(html: str) -> str:
    html = html.strip()

    if html.startswith("```html"):
        html = html.replace("```html", "", 1).strip()
    elif html.startswith("```"):
        html = html.replace("```", "", 1).strip()

    if html.endswith("```"):
        html = html[:-3].strip()

    return html


@router.post("/generate-website")
def generate_website(
    req: GenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        if not req.prompt.strip():
            raise HTTPException(status_code=400, detail="Prompt cannot be empty")

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a professional web developer. "
                        "Generate a complete, modern, responsive HTML webpage. "
                        "Include CSS styling inside <style> tags. "
                        "ONLY return valid HTML. Do not wrap the output in markdown code fences."
                    ),
                },
                {
                    "role": "user",
                    "content": req.prompt,
                },
            ],
        )

        html = response.choices[0].message.content or "<h1>No content generated</h1>"
        html = clean_generated_html(html)

        new_site = GeneratedSite(
            user_id=current_user.id,
            prompt=req.prompt,
            html=html,
        )

        db.add(new_site)
        db.commit()
        db.refresh(new_site)

        return {"html": html}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Website generation failed: {str(e)}",
        )


# =========================
# SITE PREVIEW (UPDATED FOR DASHBOARD)
# =========================

@router.get("/site/{site_id}")
def get_site(
    site_id: str,
    token: str = Query(None),  # 👈 allow token via query param
    db: Session = Depends(get_db),
):
    if not token:
        raise HTTPException(status_code=401, detail="Token required")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")

        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")

        user = db.query(User).filter(User.email == email).first()

        if not user:
            raise HTTPException(status_code=401, detail="User not found")

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    site = db.query(GeneratedSite).filter(
        GeneratedSite.id == site_id,
        GeneratedSite.user_id == user.id,
    ).first()

    if not site:
        raise HTTPException(status_code=404, detail="Site not found")

    if not site.html:
        raise HTTPException(status_code=500, detail="Site content missing")

    html = clean_generated_html(site.html)

    return Response(content=html, media_type="text/html")


# =========================
# USER HISTORY
# =========================

@router.get("/my-sites")
def get_my_sites(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sites = (
        db.query(GeneratedSite)
        .filter(GeneratedSite.user_id == current_user.id)
        .order_by(GeneratedSite.created_at.desc(), GeneratedSite.id.desc())
        .all()
    )

    return [
        {
            "id": str(site.id),
            "prompt": site.prompt,
            "created_at": site.created_at,
        }
        for site in sites
    ]
