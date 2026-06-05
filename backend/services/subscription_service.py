from sqlalchemy.orm import Session

from backend.core.subscription_tiers import (
    SUBSCRIPTION_TIERS,
)

from backend.models.subscription import Subscription
from backend.models.user import User


PREMIUM_STATUSES = {
    "active",
    "trialing",
}


class SubscriptionService:

    def __init__(self, db: Session):

        self.db = db

    # ---------------------------------------------------
    # SUBSCRIPTION LOOKUP
    # ---------------------------------------------------

    def get_user_subscription(
        self,
        user_id: int,
    ) -> Subscription | None:

        return (
            self.db.query(Subscription)
            .filter(
                Subscription.user_id == user_id
            )
            .order_by(
                Subscription.created_at.desc()
            )
            .first()
        )

    # ---------------------------------------------------
    # ACTIVE SUBSCRIPTION CHECK
    # ---------------------------------------------------

    def has_active_subscription(
        self,
        user_id: int,
    ) -> bool:

        subscription = self.get_user_subscription(
            user_id
        )

        if not subscription:

            return False

        return (
            subscription.status
            in PREMIUM_STATUSES
        )

    # ---------------------------------------------------
    # APPLY SUBSCRIPTION TIER QUOTAS
    # ---------------------------------------------------

    def apply_subscription_tier(
        self,
        user: User,
    ) -> None:
        """
        Apply quota settings based on subscription tier.
        """

        tier = user.subscription_tier

        if tier not in SUBSCRIPTION_TIERS:

            tier = "free"

        config = SUBSCRIPTION_TIERS[tier]

        user.monthly_token_quota = config[
            "monthly_token_quota"
        ]

        user.monthly_spend_quota_usd = config[
            "monthly_spend_quota_usd"
        ]
