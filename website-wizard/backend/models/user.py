import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.database import Base

# 🔥 Prevent circular imports at runtime
if TYPE_CHECKING:
    from backend.models.refresh_token import RefreshToken
    from backend.models.role import Role


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    email: Mapped[str] = mapped_column(
        String,
        unique=True,
        index=True,
        nullable=False
    )

    hashed_password: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    # ✅ Relationships (safe via string refs)
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    roles: Mapped[list["Role"]] = relationship(
        "Role",
        secondary="user_roles",
        back_populates="users"
    )