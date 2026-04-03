from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, ConfigDict


class UserRegister(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: UUID
    email: EmailStr
    is_active: bool
    is_superuser: bool

    model_config = ConfigDict(from_attributes=True)


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RefreshTokenOut(BaseModel):
    id: UUID
    jti: str
    expires_at: datetime
    revoked: bool

    model_config = ConfigDict(from_attributes=True)