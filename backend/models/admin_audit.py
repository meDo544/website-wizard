import uuid
from datetime import datetime

from sqlalchemy import (
    Column,
    String,
    DateTime,
    ForeignKey,
)

from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from backend.db.session import Base


class AdminAudit(Base):
    __tablename__ = "admin_audits"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    # ---------------------------------
    # User responsible
    # ---------------------------------

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )

    # ---------------------------------
    # Action metadata
    # ---------------------------------

    action = Column(
        String,
        nullable=False,
        index=True,
    )

    entity_type = Column(
        String,
        nullable=True,
        index=True,
    )

    entity_id = Column(
        String,
        nullable=True,
    )

    # ---------------------------------
    # Extra structured metadata
    # ---------------------------------

    metadata_json = Column(
        JSONB,
        nullable=True,
    )

    # ---------------------------------
    # Timestamp
    # ---------------------------------

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True,
    )

    # ---------------------------------
    # Relationships
    # ---------------------------------

    user = relationship("User")
