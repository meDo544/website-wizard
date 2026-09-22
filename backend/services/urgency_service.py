from typing import Any

from backend.domain.website_state import (
    WebsiteState,
)
from backend.services.business_profile_selector import (
    _business_matches,
)
from backend.services.urgency_selector import (
    select_urgency_variant,
)


def _apply_selected_urgency(
    profile: dict[str, Any],
    state: WebsiteState,
) -> None:

    selected_urgency = (
        select_urgency_variant(
            urgency_variants=profile.get(
                "urgency_variants",
                [],
            ),
            conversion_strategy=profile.get(
                "conversion_strategy",
                "general",
            ),
        )
    )

    state.urgency.selected_urgency_type = (
        selected_urgency["type"]
    )

    state.urgency.selected_urgency = (
        selected_urgency
    )

    profile[
        "selected_urgency_type"
    ] = selected_urgency["type"]

    profile[
        "selected_urgency"
    ] = selected_urgency


def _enforce_urgency_priority_rules(
    profile: dict[str, Any],
    state: WebsiteState,
) -> None:

    website_identity = profile.get(
        "website_identity",
        {},
    )

    business_type = str(
        website_identity.get(
            "business_type",
            "",
        )
    ).lower()

    urgency = (
        state.urgency.selected_urgency
    )

    if not isinstance(
        urgency,
        dict,
    ):
        return

    headline = str(
        urgency.get(
            "headline",
            "",
        )
    )

    if _business_matches(
        business_type,
        "ecommerce",
        "shop",
        "store",
        "marketplace",
        "retail",
    ):
        urgency["type"] = "limited_stock"

    elif _business_matches(
        business_type,
        "consult",
        "coach",
        "advisor",
    ):
        urgency["type"] = "limited_slots"

    elif _business_matches(
        business_type,
        "medical",
        "clinic",
        "doctor",
        "dentist",
        "health",
    ):
        urgency["type"] = "appointments"

    elif _business_matches(
        business_type,
        "restaurant",
        "cafe",
        "food",
    ):
        urgency["type"] = "today"

    elif _business_matches(
        business_type,
        "contractor",
        "construction",
        "roofing",
        "plumbing",
        "electrician",
    ):
        urgency["type"] = "seasonal"

    headline = headline.strip()

    if headline:
        urgency["headline"] = headline

    state.urgency.selected_urgency_type = (
        urgency["type"]
    )

    state.urgency.selected_urgency = urgency

    profile[
        "selected_urgency_type"
    ] = urgency["type"]

    profile[
        "selected_urgency"
    ] = urgency


def apply_urgency(
    profile: dict[str, Any],
    state: WebsiteState,
) -> None:

    _apply_selected_urgency(
        profile,
        state,
    )

    _enforce_urgency_priority_rules(
        profile,
        state,
    )
