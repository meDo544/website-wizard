import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean
from sqlalchemy import ForeignKey
from sqlalchemy import Integer

from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from backend.db.session import Base


# ---------------------------------------------------
# Prevent circular imports
# ---------------------------------------------------

if TYPE_CHECKING:
    from backend.models.plan import Plan


class PlanFeature(Base):
    __tablename__ = "plan_features"

    # ---------------------------------------------------
    # Columns
    # ---------------------------------------------------

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("plans.id"),
        nullable=False,
        unique=True,
    )

    # ---------------------------------------------------
    # Feature flags
    # ---------------------------------------------------

    can_publish: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    can_use_custom_domain: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    can_export: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    # ---------------------------------------------------
    # Usage limits
    # ---------------------------------------------------

    max_sites: Mapped[int] = mapped_column(
        Integer,
        default=1,
    )

    max_ai_credits: Mapped[int] = mapped_column(
        Integer,
        default=10,
    )

    # ---------------------------------------------------
    # Relationships
    # ---------------------------------------------------

    plan: Mapped["Plan"] = relationship(
        "Plan",
        back_populates="features",
    )
