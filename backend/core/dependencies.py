from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from backend.core.database import SessionLocal
from backend.core.security import SECRET_KEY, ALGORITHM


# =========================
# DATABASE
# =========================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# AUTH (PRODUCTION-READY)
# =========================

def get_current_user(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")

    parts = authorization.split(" ")

    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    token = parts[1]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")

        if not email:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        return {
            "email": email,
            "status": "token_valid",
        }

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# =========================
# AUTH HELPERS (PLACEHOLDER — CLEAN)
# =========================

def require_roles(*required_roles: str):
    def dependency(current_user=Depends(get_current_user)):
        return current_user
    return dependency


def require_permissions(*required_permissions: str):
    def dependency(current_user=Depends(get_current_user)):
        return current_user
    return dependency
