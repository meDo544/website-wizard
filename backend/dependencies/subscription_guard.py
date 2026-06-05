from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from backend.core.database import SessionLocal
from backend.models.user import User

from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer

import os
import uuid

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "dev-secret-key-change-in-production",
)

ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/login"
)


def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


def require_active_subscription(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        user_id = payload.get("sub")

        if not user_id:

            raise HTTPException(
                status_code=401,
                detail="Invalid token",
            )

        user_uuid = uuid.UUID(user_id)

    except (JWTError, ValueError):

        raise HTTPException(
            status_code=401,
            detail="Invalid token",
        )

    user = (
        db.query(User)
        .filter(User.id == user_uuid)
        .first()
    )

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    # --------------------------------
    # SUBSCRIPTION STATUS CHECK
    # --------------------------------

    if user.subscription_status != "active":

        raise HTTPException(
            status_code=403,
            detail="Subscription inactive",
        )

    # --------------------------------
    # TOKEN QUOTA CHECK
    # --------------------------------

    if (
        user.monthly_tokens_used
        >= user.monthly_token_quota
    ):

        raise HTTPException(
            status_code=403,
            detail="Monthly token quota exceeded",
        )

    return user
