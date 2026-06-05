import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean
from sqlalchemy import String

from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from backend.db.session import Base

# ---------------------------------------------------
# 🔥 IMPORTANT:
# Runtime import REQUIRED for SQLAlchemy registry
# ---------------------------------------------------

from backend.models.plan_feature import PlanFeature

# Prevent circular imports in typing only
if TYPE_CHECKING:
    from backend.models.subscription import Subscription


class Plan(Base):
    __tablename__ = "plans"

    # ---------------------------------------------------
    # Columns
    # ---------------------------------------------------

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    name: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    # ---------------------------------------------------
    # Relationships
    # ---------------------------------------------------

    subscriptions: Mapped[list["Subscription"]] = relationship(
        "Subscription",
        back_populates="plan",
    )

    features: Mapped["PlanFeature"] = relationship(
        "PlanFeature",
        back_populates="plan",
        uselist=False,
        cascade="all, delete-orphan",
    )
