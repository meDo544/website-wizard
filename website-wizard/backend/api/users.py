from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from backend.core.database import SessionLocal
from backend.models.user import User
from backend.schemas.auth import UserOut
from backend.deps.auth import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


# =========================
# DB Dependency
# =========================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# Get Current User Profile
# =========================
@router.get("/me", response_model=UserOut)
def get_my_profile(
    current_user: User = Depends(get_current_user),
):
    return current_user


# =========================
# Get All Users (Protected)
# =========================
@router.get("/", response_model=List[UserOut])
def get_all_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(User).all()