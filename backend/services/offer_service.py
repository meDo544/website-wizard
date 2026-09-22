from typing import Any

from backend.domain.website_state import WebsiteState

from backend.services.business_profile_selector import (
    _business_matches,
)

from backend.services.offer_selector import (
    _normalize_offer_variants,
    normalize_offer_type,
    select_offer_variant,
)


def _apply_selected_offer(
    profile: dict[str, Any],
    state: WebsiteState,
) -> None:

    selected_offer = select_offer_variant(
        offer_variants=profile.get(
            "offer_variants",
            [],
        ),
        conversion_strategy=profile.get(
            "conversion_strategy",
            "general",
        ),
    )

    state.offer.selected_offer_type = (
        selected_offer["type"]
    )

    state.offer.selected_offer = (
        selected_offer
    )

    state.offer.offer_title = (
        selected_offer.get(
            "headline",
            "",
        )
    )

    state.offer.offer_subtitle = (
        selected_offer.get(
            "subtitle",
            "",
        )
    )


def _enforce_offer_priority_rules(
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

    offer = state.offer.selected_offer

    if not isinstance(
        offer,
        dict,
    ):
        return

    headline = str(
        offer.get(
            "headline",
            "",
        )
    )

    # Ecommerce
    if _business_matches(
        business_type,
        "ecommerce",
        "shop",
        "store",
        "marketplace",
        "retail",
    ):
        offer["type"] = "discount"
        state.offer.selected_offer_type = "discount"

    # Consultant
    elif _business_matches(
        business_type,
        "consult",
        "coach",
        "advisor",
    ):
        offer["type"] = "consultation"
        state.offer.selected_offer_type = "consultation"

    # Restaurant
    elif _business_matches(
        business_type,
        "restaurant",
        "cafe",
        "food",
    ):
        offer["type"] = "discount"
        state.offer.selected_offer_type = "discount"

    offer["headline"] = headline
    state.offer.selected_offer = offer


def apply_offer(
    profile: dict[str, Any],
    state: WebsiteState,
) -> None:
    _normalize_offer_variants(
        profile,
    )

    _apply_selected_offer(
        profile,
        state,
    )

    _enforce_offer_priority_rules(
        profile,
        state,
    )

    profile.update(
        state.offer.to_dict()
    )

