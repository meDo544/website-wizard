from backend.models.usage import Usage


class UsageService:
    """
    Handles SaaS usage tracking.

    Tracks:
    - sites created
    - AI credits consumed
    """

    def __init__(self, db):
        self.db = db

    # ---------------------------------
    # Get or create usage row
    # ---------------------------------

    def get_or_create_usage(
        self,
        user_id,
    ):
        usage = (
            self.db.query(Usage)
            .filter(
                Usage.user_id == user_id
            )
            .first()
        )

        if not usage:

            usage = Usage(
                user_id=user_id,

                sites_created=0,

                ai_credits_used=0,
            )

            self.db.add(usage)

            self.db.commit()

            self.db.refresh(usage)

        return usage

    # ---------------------------------
    # Increment site count
    # ---------------------------------

    def increment_sites(
        self,
        user_id,
    ):
        usage = self.get_or_create_usage(
            user_id
        )

        usage.sites_created += 1

        self.db.commit()

        return usage

    # ---------------------------------
    # Increment AI credits
    # ---------------------------------

    def increment_ai_credits(
        self,
        user_id,
        amount=1,
    ):
        usage = self.get_or_create_usage(
            user_id
        )

        usage.ai_credits_used += amount

        self.db.commit()

        return usage

    # ---------------------------------
    # Record GPT usage
    # ---------------------------------

    def record_gpt_usage(
        self,
        user,
        tokens_used: int,
        estimated_cost_usd: float,
    ):

        # User-level metering
        user.monthly_tokens_used += (
            tokens_used
        )

        user.monthly_spend_used_usd += (
            estimated_cost_usd
        )

        user.monthly_request_count += 1

        # Legacy usage tracking
        usage = self.get_or_create_usage(
            user.id
        )

        usage.ai_credits_used += 1

        self.db.commit()

        self.db.refresh(user)

        return user
