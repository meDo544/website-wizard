from typing import Any

from backend.domain.website_state import WebsiteState

from backend.services.business_profile_selector import (
    _business_matches,
)

from backend.services.trust_selector import (
    _normalize_trust_variants,
    select_trust_variant,
)


def _apply_selected_trust(
    profile: dict[str, Any],
    state: WebsiteState,
) -> None:

    selected_trust = select_trust_variant(
        trust_variants=profile.get(
            "trust_variants",
            [],
        ),
        conversion_strategy=profile.get(
            "conversion_strategy",
            "general",
        ),
    )

    state.trust.selected_trust_type = (
        selected_trust["type"]
    )

    state.trust.selected_trust = (
        selected_trust
    )


def _enforce_trust_priority_rules(
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

    trust = state.trust.selected_trust

    if not isinstance(
        trust,
        dict,
    ):
        return

    headline = str(
        trust.get(
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
        trust["type"] = "reviews"
        state.trust.selected_trust_type = "reviews"

    # Consultant
    elif _business_matches(
        business_type,
        "consult",
        "coach",
        "advisor",
    ):
        trust["type"] = "experience"
        state.trust.selected_trust_type = "experience"

    # Medical
    elif _business_matches(
        business_type,
        "medical",
        "clinic",
        "dentist",
        "doctor",
        "health",
    ):
        trust["type"] = "certification"
        state.trust.selected_trust_type = "certification"

    # Contractor
    elif _business_matches(
        business_type,
        "contractor",
        "construction",
        "roofing",
        "plumbing",
        "electrician",
    ):
        trust["type"] = "guarantee"
        state.trust.selected_trust_type = "guarantee"

    trust["headline"] = headline
    state.trust.selected_trust = trust


def apply_trust(
    profile: dict[str, Any],
    state: WebsiteState,
) -> None:

    _normalize_trust_variants(
        profile,
    )

    _apply_selected_trust(
        profile,
        state,
    )

    _enforce_trust_priority_rules(
        profile,
        state,
    )

    profile.update(
        state.trust.to_dict()
    )
