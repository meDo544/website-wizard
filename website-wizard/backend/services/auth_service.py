from jose import JWTError, jwt
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from uuid import UUID

from backend.core.exceptions import (
    ConflictException,
    UnauthorizedException,
    ForbiddenException,
)
from backend.core.security import (
    ALGORITHM,
    SECRET_KEY,
    create_access_token,
    create_refresh_token,
    hash_password,
    hash_token,
    verify_password,
)
from backend.models.refresh_token import RefreshToken
from backend.models.user import User


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db

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

    def authenticate_user(self, email: str, password: str) -> User:
        user = self.db.query(User).filter(User.email == email).first()
        if not user or not verify_password(password, user.hashed_password):
            raise UnauthorizedException("Invalid credentials", code="invalid_credentials")
        if not user.is_active:
            raise ForbiddenException("User is inactive", code="inactive_user")
        return user

    def issue_token_pair(self, user: User, user_agent: str | None = None, ip_address: str | None = None) -> dict:
        access_token = create_access_token(
            subject=str(user.id),
            extra_claims={
                "roles": [role.name for role in user.roles],
                "is_superuser": user.is_superuser,
            },
        )
        refresh_token, jti, expires_at = create_refresh_token(subject=str(user.id))

        db_token = RefreshToken(
            user_id=user.id,
            jti=jti,
            token_hash=hash_token(refresh_token),
            expires_at=expires_at,
            user_agent=user_agent,
            ip_address=ip_address,
            revoked=False,
        )
        self.db.add(db_token)
        self.db.commit()

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    def refresh_access_token(self, raw_refresh_token: str) -> dict:
        try:
            payload = jwt.decode(raw_refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        except JWTError:
            raise UnauthorizedException("Invalid refresh token", code="invalid_refresh_token")

        if payload.get("type") != "refresh":
            raise UnauthorizedException("Invalid token type", code="invalid_token_type")

        sub = payload.get("sub")
        jti = payload.get("jti")

        if not sub or not jti:
            raise UnauthorizedException("Invalid refresh token payload", code="invalid_refresh_payload")

        db_token = (
            self.db.query(RefreshToken)
            .filter(RefreshToken.jti == jti)
            .first()
        )

        if not db_token or db_token.revoked:
            raise UnauthorizedException("Refresh token revoked", code="refresh_revoked")

        if db_token.token_hash != hash_token(raw_refresh_token):
            raise UnauthorizedException("Refresh token mismatch", code="refresh_mismatch")

        user = self.db.query(User).filter(User.id == UUID(sub)).first()
        if not user or not user.is_active:
            raise UnauthorizedException("User not available", code="user_invalid")

        # rotation: revoke old refresh token, issue new pair
        db_token.revoked = True
        self.db.add(db_token)
        self.db.commit()

        return self.issue_token_pair(user)

    def revoke_refresh_token(self, raw_refresh_token: str) -> None:
        try:
            payload = jwt.decode(raw_refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        except JWTError:
            raise UnauthorizedException("Invalid refresh token", code="invalid_refresh_token")

        jti = payload.get("jti")
        if not jti:
            raise UnauthorizedException("Invalid refresh token payload", code="invalid_refresh_payload")

        db_token = self.db.query(RefreshToken).filter(RefreshToken.jti == jti).first()
        if db_token:
            db_token.revoked = True
            self.db.add(db_token)
            self.db.commit()