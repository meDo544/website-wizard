from fastapi import APIRouter, Depends, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from backend.core.dependencies import get_db, get_current_user
from backend.models.user import User
from backend.schemas.auth import (
    RefreshTokenRequest,
    Token,
    TokenPair,
    UserOut,
    UserRegister,
)
from backend.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    service = AuthService(db)
    user = service.register_user(payload.email, payload.password)
    return user


@router.post("/login", response_model=TokenPair)
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    service = AuthService(db)
    user = service.authenticate_user(form_data.username, form_data.password)

    user_agent = request.headers.get("user-agent")
    ip_address = request.client.host if request.client else None

    return service.issue_token_pair(user, user_agent=user_agent, ip_address=ip_address)


@router.post("/refresh", response_model=TokenPair)
def refresh(payload: RefreshTokenRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    return service.refresh_access_token(payload.refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(payload: RefreshTokenRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    service.revoke_refresh_token(payload.refresh_token)
    return None


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user