import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from backend.core.database import Base


class Audit(Base):
    __tablename__ = "audits"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    url = Column(String, nullable=False)

    status = Column(String, nullable=False, default="queued")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    completed_at = Column(DateTime, nullable=True)

    error_message = Column(Text, nullable=True)

    result_json = Column(JSONB, nullable=True)

    user = relationship("User", back_populates="audits")
