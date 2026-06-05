# backend/models/user.py

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import (
    Column,
    Float,
    Integer,
    String,
)

from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from backend.db.session import Base

# ------------------------------------------------------------------
# TYPE CHECKING IMPORTS
# Prevent circular imports at runtime
# ------------------------------------------------------------------

if TYPE_CHECKING:

    from backend.models.generated_sites import GeneratedSite
    from backend.models.refresh_token import RefreshToken
    from backend.models.role import Role
    from backend.models.subscription import Subscription


class User(Base):

    __tablename__ = "users"

    subscription_status = Column(
        String,
        default="active",
    )

    # ------------------------------------------------------------------
    # CORE FIELDS
    # ------------------------------------------------------------------

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    email: Mapped[str] = mapped_column(
        String,
        unique=True,
        index=True,
        nullable=False,
    )

    hashed_password: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    # ------------------------------------------------------------------
    # STRIPE INTEGRATION
    # ------------------------------------------------------------------

    stripe_customer_id: Mapped[str | None] = mapped_column(
        String,
        unique=True,
        index=True,
        nullable=True,
    )

    # ------------------------------------------------------------------
    # AI SUBSCRIPTION / QUOTAS
    # ------------------------------------------------------------------

    subscription_tier = Column(
        String(50),
        nullable=False,
        default="free",
    )

    monthly_token_quota = Column(
        Integer,
        nullable=False,
        default=100000,
    )

    monthly_spend_quota_usd = Column(
        Float,
        nullable=False,
        default=10.0,
    )

    monthly_tokens_used = Column(
        Integer,
        nullable=False,
        default=0,
    )

    monthly_spend_used_usd = Column(
        Float,
        nullable=False,
        default=0.0,
    )

    monthly_request_count = Column(
        Integer,
        nullable=False,
        default=0,
    )

    # ------------------------------------------------------------------
    # RELATIONSHIPS
    # ------------------------------------------------------------------

    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    roles: Mapped[list["Role"]] = relationship(
        "Role",
        secondary="user_roles",
        back_populates="users",
    )

    subscriptions: Mapped[list["Subscription"]] = relationship(
        "Subscription",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    generated_sites: Mapped[list["GeneratedSite"]] = relationship(
        "GeneratedSite",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select",
    )

    # ------------------------------------------------------------------
    # REPRESENTATION
    # ------------------------------------------------------------------

    def __repr__(self) -> str:

        return (
            f"<User("
            f"id={self.id}, "
            f"email={self.email}, "
            f"tier={self.subscription_tier}"
            f")>"
        )
