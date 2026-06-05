# backend/models/subscription.py

from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from backend.db.session import Base


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # 🔹 Owner
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # 🔹 Stripe identifiers
    stripe_customer_id = Column(String, nullable=False, index=True)
    stripe_subscription_id = Column(String, nullable=False, unique=True, index=True)
    stripe_price_id = Column(String, nullable=True, index=True)

    # 🔹 Internal plan mapping
    plan_id = Column(UUID(as_uuid=True), ForeignKey("plans.id"), nullable=True)

    # 🔹 Subscription status (Stripe-driven)
    status = Column(String, nullable=False, index=True)  # active, canceled, past_due, etc.

    # 🔹 Relationships
    user = relationship("User", back_populates="subscriptions")
    plan = relationship("Plan", back_populates="subscriptions")
