import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from jose import jwt
from passlib.context import CryptContext

SECRET_KEY = "change-me"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_access_token(subject: str, extra_claims: dict | None = None) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp()),
        "jti": str(uuid4()),
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(subject: str) -> tuple[str, str, datetime]:
    now = datetime.now(timezone.utc)
    jti = str(uuid4())
    expires_at = now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    payload = {
        "sub": subject,
        "type": "refresh",
        "iat": int(now.timestamp()),
        "exp": int(expires_at.timestamp()),
        "jti": jti,
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token, jti, expires_at