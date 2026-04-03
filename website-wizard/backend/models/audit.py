import uuid

from sqlalchemy import Column, String, DateTime, Text, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func

from backend.core.database import Base


class Audit(Base):
    __tablename__ = "audits"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # ✅ FK → users.id (UUID)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)

    url = Column(String, nullable=False, index=True)
    status = Column(String, nullable=False, default="queued", index=True)

    # worker control
    retry_count = Column(Integer, nullable=False, default=0)
    claimed_by = Column(String, nullable=True)
    heartbeat_at = Column(DateTime(timezone=True), nullable=True)
    last_error_at = Column(DateTime(timezone=True), nullable=True)

    # scores
    overall_score = Column(Integer, nullable=True)
    performance_score = Column(Integer, nullable=True)
    seo_score = Column(Integer, nullable=True)
    accessibility_score = Column(Integer, nullable=True)
    best_practices_score = Column(Integer, nullable=True)

    # payloads
    crawl_data = Column(JSONB, nullable=True)
    lighthouse_data = Column(JSONB, nullable=True)
    gpt_report = Column(JSONB, nullable=True)
    error_message = Column(Text, nullable=True)

    # timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)