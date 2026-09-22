from typing import Any

from backend.domain.website_state import WebsiteState


VALID_CONVERSION_STRATEGIES = {
    "restaurant",
    "saas",
    "consultant",
    "contractor",
    "agency",
    "medical",
    "ecommerce",
    "purchase",
    "general",
}


def _normalize_conversion_strategy(
    profile: dict[str, Any],
) -> None:

    website_identity = profile.get(
        "website_identity",
        {},
    )

    strategy = str(
        website_identity.get(
            "cta_strategy",
            profile.get(
                "conversion_strategy",
                "general",
            ),
        )
    ).lower()

    if strategy not in VALID_CONVERSION_STRATEGIES:
        strategy = "general"

    profile["conversion_strategy"] = strategy

    if isinstance(
        website_identity,
        dict,
    ):
        website_identity[
            "cta_strategy"
        ] = strategy


def apply_conversion_strategy(
    profile: dict[str, Any],
    state: WebsiteState,
) -> None:

    _normalize_conversion_strategy(
        profile
    )

    strategy = str(
        profile.get(
            "conversion_strategy",
            "general",
        )
    )

    website_identity = profile.get(
        "website_identity",
        {},
    )

    if not isinstance(
        website_identity,
        dict,
    ):
        website_identity = {}

    state.conversion_strategy.conversion_strategy = (
        strategy
    )

    state.conversion_strategy.website_identity = dict(
        website_identity
    )
