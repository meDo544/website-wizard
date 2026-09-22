from typing import Any

from backend.domain.website_state import WebsiteState

from backend.services.business_profile_selector import (
    _business_matches,
)

from backend.services.risk_reversal_selector import (
    _normalize_risk_reversal_variants,
    select_risk_reversal_variant,
)


def _apply_selected_risk_reversal(
    profile: dict[str, Any],
    state: WebsiteState,
) -> None:

    selected_risk_reversal = (
        select_risk_reversal_variant(
            risk_reversal_variants=profile.get(
                "risk_reversal_variants",
                [],
            ),
            conversion_strategy=profile.get(
                "conversion_strategy",
                "general",
            ),
        )
    )

    state.risk_reversal.selected_risk_reversal_type = (
        selected_risk_reversal["type"]
    )

    state.risk_reversal.selected_risk_reversal = (
        selected_risk_reversal
    )


def enforce_risk_reversal_priority_rules(
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

    risk_reversal = (
        state.risk_reversal.selected_risk_reversal
    )

    if not isinstance(
        risk_reversal,
        dict,
    ):
        return

    headline = str(
        risk_reversal.get(
            "headline",
            "",
        )
    )

    # Restaurant
    if _business_matches(
        business_type,
        "restaurant",
        "cafe",
        "food",
        "pizza",
        "bakery",
    ):
        risk_reversal["type"] = "freshness"

        state.risk_reversal.selected_risk_reversal_type = (
            "freshness"
        )

    # Ecommerce
    elif _business_matches(
        business_type,
        "ecommerce",
        "shop",
        "store",
        "marketplace",
        "retail",
    ):
        risk_reversal["type"] = "guarantee"

        state.risk_reversal.selected_risk_reversal_type = (
            "guarantee"
        )

    # Consultant
    elif _business_matches(
        business_type,
        "consult",
        "coach",
        "advisor",
    ):
        risk_reversal["type"] = "consultation"

        state.risk_reversal.selected_risk_reversal_type = (
            "consultation"
        )

    # Medical
    elif _business_matches(
        business_type,
        "medical",
        "clinic",
        "doctor",
        "dentist",
        "health",
    ):
        risk_reversal["type"] = "assurance"

        state.risk_reversal.selected_risk_reversal_type = (
            "assurance"
        )

    # Contractor
    elif _business_matches(
        business_type,
        "contractor",
        "construction",
        "roofing",
        "plumbing",
        "electrician",
    ):
        risk_reversal["type"] = "warranty"

        state.risk_reversal.selected_risk_reversal_type = (
            "warranty"
        )

    risk_reversal["headline"] = headline

    state.risk_reversal.selected_risk_reversal = (
        risk_reversal
    )


def apply_risk_reversal(
    profile: dict[str, Any],
    state: WebsiteState,
) -> None:

    _normalize_risk_reversal_variants(
        profile,
    )

    _apply_selected_risk_reversal(
        profile,
        state,
    )

    enforce_risk_reversal_priority_rules(
        profile,
        state,
    )

    profile.update(
        state.risk_reversal.to_dict()
    )
