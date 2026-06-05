from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import traceback

from backend.core.database import get_db
from backend.models.user import User
from backend.schemas.auth import UserRegister, UserOut
from backend.core.security import (
    hash_password,
    verify_password,
    create_access_token,
)
from backend.dependencies.auth import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

# ---------------------------------------------------
# REGISTER
# ---------------------------------------------------
@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
)
def register(
    payload: UserRegister,
    db: Session = Depends(get_db),
) -> UserOut:
    """
    Register a new user account. Raises 400 if the email already exists.
    """
    existing_user = (
        db.query(User)
        .filter(User.email == payload.email)
        .first()
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    try:
        user = User(
            email=payload.email,
            hashed_password=hash_password(payload.password),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return UserOut.model_validate(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    except Exception:
        db.rollback()
        # Log the error and return a generic message
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred.",
        )

# ---------------------------------------------------
# LOGIN
# ---------------------------------------------------
@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Authenticate a user and return a JWT access token.
    The `username` field of the form is treated as the user's email.
    """
    user = (
        db.query(User)
        .filter(User.email == form_data.username)
        .first()
    )
    if not user or not verify_password(
        form_data.password,
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    # Issue a token using the user ID as the subject
    access_token = create_access_token(str(user.id))
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }

# ---------------------------------------------------
# CURRENT USER ROUTE
# ---------------------------------------------------
@router.get("/me")
def read_me(
    current_user: User = Depends(get_current_user),
):
    """
    Return the current authenticated user's profile and subscription info.
    """
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "subscription_tier": current_user.subscription_tier,
        "subscription_status": current_user.subscription_status,
        "monthly_token_quota": current_user.monthly_token_quota,
        "monthly_tokens_used": current_user.monthly_tokens_used,
        "monthly_spend_quota_usd": current_user.monthly_spend_quota_usd,
        "monthly_spend_used_usd": current_user.monthly_spend_used_usd,
        "monthly_request_count": current_user.monthly_request_count,
        "stripe_customer_id": current_user.stripe_customer_id,
    }
