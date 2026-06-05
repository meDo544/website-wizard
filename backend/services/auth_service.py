from jose import JWTError, jwt
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from backend.core.exceptions import (
    ConflictException,
    UnauthorizedException,
)
from backend.core.security import (
    ALGORITHM,
    SECRET_KEY,
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password as core_verify_password,
)
from backend.models.user import User


# ---------------------------------------------------
# SAFE PASSWORD VERIFY (CRITICAL FIX)
# ---------------------------------------------------
def safe_verify_password(plain_password: str, hashed_password: str) -> bool:
    if not plain_password or not hashed_password:
        return False

    # bcrypt safety limit (72 bytes)
    if len(plain_password.encode("utf-8")) > 72:
        plain_password = plain_password[:72]

    try:
        return core_verify_password(plain_password, hashed_password)
    except Exception:
        return False


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db

    # ---------------------------------------------------
    # REGISTER
    # ---------------------------------------------------
    def register_user(self, email: str, password: str) -> User:
        user = User(
            email=email,
            hashed_password=hash_password(password),
        )

        self.db.add(user)

        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise ConflictException("Email already registered", code="email_exists")

        self.db.refresh(user)
        return user

    # ---------------------------------------------------
    # LOGIN
    # ---------------------------------------------------
    def authenticate_user(self, email: str, password: str) -> User:
        user = self.db.query(User).filter(User.email == email).first()

        if not user:
            raise UnauthorizedException("Invalid credentials", code="invalid_credentials")

        # ✅ SAFE PASSWORD CHECK (FIXED)
        password_ok = safe_verify_password(password, user.hashed_password)

        if not password_ok:
            raise UnauthorizedException("Invalid credentials", code="invalid_credentials")

        return user

    # ---------------------------------------------------
    # TOKEN ISSUANCE
    # ---------------------------------------------------
    def issue_token_pair(
        self,
        user: User,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> dict:
        access_token = create_access_token(
            subject=user.email,
        )

        refresh_token, jti, expires_at = create_refresh_token(
            subject=user.email
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    # ---------------------------------------------------
    # REFRESH TOKEN
    # ---------------------------------------------------
    def refresh_access_token(self, raw_refresh_token: str) -> dict:
        try:
            payload = jwt.decode(raw_refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        except JWTError:
            raise UnauthorizedException("Invalid refresh token", code="invalid_refresh_token")

        if payload.get("type") != "refresh":
            raise UnauthorizedException("Invalid token type", code="invalid_token_type")

        sub = payload.get("sub")

        if not sub:
            raise UnauthorizedException("Invalid refresh token payload", code="invalid_refresh_payload")

        user = self.db.query(User).filter(User.email == sub).first()

        if not user:
            raise UnauthorizedException("User not available", code="user_invalid")

        return self.issue_token_pair(user)

    # ---------------------------------------------------
    # REVOKE (NO-OP)
    # ---------------------------------------------------
    def revoke_refresh_token(self, raw_refresh_token: str) -> None:
        return
