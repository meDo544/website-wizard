from backend.models.user import User


def check_user_quota(user: User) -> tuple[bool, str]:
    """
    Validate whether the user can continue making GPT requests.
    """

    # ---------------------------------------------------
    # TOKEN QUOTA
    # ---------------------------------------------------

    if user.monthly_tokens_used >= user.monthly_token_quota:

        return (
            False,
            "Monthly token quota exceeded.",
        )

    # ---------------------------------------------------
    # SPEND QUOTA
    # ---------------------------------------------------

    if (
        user.monthly_spend_used_usd
        >= user.monthly_spend_quota_usd
    ):

        return (
            False,
            "Monthly AI spend quota exceeded.",
        )

    # ---------------------------------------------------
    # REQUEST QUOTA
    # ---------------------------------------------------

    if user.monthly_request_count >= 1000:

        return (
            False,
            "Monthly request quota exceeded.",
        )

    return (
        True,
        "Quota check passed.",
    )
