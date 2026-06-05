# backend/models/usage.py

from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid

from backend.db.session import Base


class Usage(Base):
    __tablename__ = "usage"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # 🔥 Track usage
    ai_credits_used = Column(Integer, default=0)
    sites_created = Column(Integer, default=0)
