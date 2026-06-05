from __future__ import annotations

import uuid

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    func,
)

from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.orm import relationship

from backend.db.session import Base


class GeneratedSite(Base):

    __tablename__ = "generated_sites"

    # ---------------------------------------------------
    # PRIMARY KEY
    # ---------------------------------------------------

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        index=True,
    )

    # ---------------------------------------------------
    # USER RELATIONSHIP
    # ---------------------------------------------------

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    user = relationship(
        "User",
        back_populates="generated_sites",
    )

    # ---------------------------------------------------
    # WEBSITE INPUT
    # ---------------------------------------------------

    project_name = Column(
        String(255),
        nullable=True,
    )

    business_type = Column(
        String(255),
        nullable=True,
    )

    prompt = Column(
        Text,
        nullable=False,
    )

    # ---------------------------------------------------
    # GENERATED OUTPUT
    # ---------------------------------------------------

    html = Column(
        Text,
        nullable=True,
    )

    css = Column(
        Text,
        nullable=True,
    )

    js = Column(
        Text,
        nullable=True,
    )

    generated_url = Column(
        String(1000),
        nullable=True,
    )

    # ---------------------------------------------------
    # AI METRICS
    # ---------------------------------------------------

    gpt_model = Column(
        String(100),
        nullable=True,
        index=True,
    )

    gpt_tokens_prompt = Column(
        Integer,
        nullable=True,
        default=0,
    )

    gpt_tokens_completion = Column(
        Integer,
        nullable=True,
        default=0,
    )

    gpt_tokens_total = Column(
        Integer,
        nullable=True,
        default=0,
        index=True,
    )

    gpt_cost_usd = Column(
        Float,
        nullable=True,
        default=0.0,
        index=True,
    )

    # ---------------------------------------------------
    # STATUS / ERRORS
    # ---------------------------------------------------

    generation_status = Column(
        String(50),
        nullable=False,
        default="queued",
        index=True,
    )

    error_message = Column(
        Text,
        nullable=True,
    )

    # ---------------------------------------------------
    # FLEXIBLE METADATA
    # ---------------------------------------------------

    metadata_json = Column(
        JSON,
        nullable=True,
    )

    # ---------------------------------------------------
    # TIMESTAMPS
    # ---------------------------------------------------

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # ---------------------------------------------------
    # REPRESENTATION
    # ---------------------------------------------------

    def __repr__(self) -> str:

        return (
            f"<GeneratedSite("
            f"id={self.id}, "
            f"status={self.generation_status}, "
            f"project={self.project_name}"
            f")>"
        )


# ---------------------------------------------------
# LEGACY COMPATIBILITY
# ---------------------------------------------------

WebsiteRecord = GeneratedSite
