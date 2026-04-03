from uuid import UUID

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from backend.core.database import SessionLocal
from backend.core.exceptions import UnauthorizedException, ForbiddenException
from backend.core.security import SECRET_KEY, ALGORITHM
from backend.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "access":
            raise UnauthorizedException("Invalid token type", code="invalid_token_type")
        sub = payload.get("sub")
        if not sub:
            raise UnauthorizedException("Invalid token payload", code="invalid_token_payload")
        user_id = UUID(sub)
    except (JWTError, ValueError):
        raise UnauthorizedException("Could not validate credentials", code="invalid_credentials")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise UnauthorizedException("Could not validate credentials", code="invalid_credentials")
    if not user.is_active:
        raise ForbiddenException("Inactive user", code="inactive_user")
    return user


def require_roles(*required_roles: str):
    def dependency(current_user: User = Depends(get_current_user)) -> User:
        user_roles = {role.name for role in current_user.roles}
        if not user_roles.intersection(required_roles) and not current_user.is_superuser:
            raise ForbiddenException("Not enough permissions", code="missing_role")
        return current_user
    return dependency


def require_permissions(*required_permissions: str):
    def dependency(current_user: User = Depends(get_current_user)) -> User:
        user_permissions = {
            permission.name
            for role in current_user.roles
            for permission in role.permissions
        }
        if not user_permissions.issuperset(required_permissions) and not current_user.is_superuser:
            raise ForbiddenException("Not enough permissions", code="missing_permission")
        return current_user
    return dependency