from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.sql import func

from backend.db.session import Base


class StripeWebhookEvent(Base):
    __tablename__ = "stripe_webhook_events"

    id = Column(String, primary_key=True, index=True)
    event_type = Column(String, nullable=False, index=True)
    status = Column(String, nullable=False, default="processed")
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
