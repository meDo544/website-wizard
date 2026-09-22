from typing import Any

from backend.domain.website_state import WebsiteState

from backend.services.business_profile_selector import (
    _business_matches,
)

from backend.services.social_proof_selector import (
    _normalize_social_proof_variants,
    select_social_proof_variant,
)


def _apply_selected_social_proof(
    profile: dict[str, Any],
    state: WebsiteState,
) -> None:

    selected_social_proof = (
        select_social_proof_variant(
            social_proof_variants=profile.get(
                "social_proof_variants",
                [],
            ),
            conversion_strategy=profile.get(
                "conversion_strategy",
                "general",
            ),
        )
    )

    state.social_proof.selected_social_proof_type = (
        selected_social_proof["type"]
    )

    state.social_proof.selected_social_proof = (
        selected_social_proof
    )


def enforce_social_proof_priority_rules(
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

    social_proof = (
        state.social_proof.selected_social_proof
    )

    if not isinstance(
        social_proof,
        dict,
    ):
        return

    headline = str(
        social_proof.get(
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
        social_proof["type"] = "reviews"
        state.social_proof.selected_social_proof_type = (
            "reviews"
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
        social_proof["type"] = "customers"
        state.social_proof.selected_social_proof_type = (
            "customers"
        )

    # Consultant
    elif _business_matches(
        business_type,
        "consult",
        "coach",
        "advisor",
    ):
        social_proof["type"] = "projects"
        state.social_proof.selected_social_proof_type = (
            "projects"
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
        social_proof["type"] = "patients"
        state.social_proof.selected_social_proof_type = (
            "patients"
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
        social_proof["type"] = "projects"
        state.social_proof.selected_social_proof_type = (
            "projects"
        )

    social_proof["headline"] = headline

    state.social_proof.selected_social_proof = (
        social_proof
    )


def apply_social_proof(
    profile: dict[str, Any],
    state: WebsiteState,
) -> None:

    _normalize_social_proof_variants(
        profile,
    )

    _apply_selected_social_proof(
        profile,
        state,
    )

    enforce_social_proof_priority_rules(
        profile,
        state,
    )

    profile.update(
        state.social_proof.to_dict()
    )
