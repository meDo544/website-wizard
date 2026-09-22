from typing import Any


SOCIAL_PROOF_STRATEGY_MAP = {
    "restaurant": ["reviews", "customers", "local"],
    "saas": ["customers", "users", "case_study"],
    "consultant": ["results", "clients", "case_study"],
    "contractor": ["projects", "reviews", "local"],
    "agency": ["clients", "case_study", "results"],
    "medical": ["patients", "reviews", "certification"],
    "general": ["customers"],
}

SOCIAL_PROOF_FALLBACK_ORDER = [
    "customers",
    "clients",
    "users",
    "projects",
    "reviews",
    "results",
    "case_study",
    "community",
    "patients",
    "local",
    "certification",
    "general",
]

SOCIAL_PROOF_TYPE_ALIASES = {
    "customer": "customers",
    "client": "clients",
    "user": "users",
     "project": "projects",
    "testimonial": "reviews",
    "testimonials": "reviews",
    "rating": "reviews",
    "ratings": "reviews",
    "proof": "results",
    "portfolio": "case_study",
    "case_studies": "case_study",
    "community_members": "community",
}


def normalize_social_proof_type(
    social_proof_type: str | None,
) -> str:

    if not social_proof_type:
        return "general"

    normalized = (
        str(social_proof_type)
        .strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )

    return SOCIAL_PROOF_TYPE_ALIASES.get(
        normalized,
        normalized,
    )


def _normalize_social_proof_variants(
    profile: dict[str, Any],
) -> None:

    variants = profile.get(
        "social_proof_variants",
        [],
    )

    if not isinstance(
        variants,
        list,
    ):
        variants = []

    normalized_variants = []

    for variant in variants:

        if not isinstance(
            variant,
            dict,
        ):
            continue

        social_proof_type = (
            normalize_social_proof_type(
                variant.get("type")
            )
        )

        headline = str(
            variant.get(
                "headline",
                "",
            )
        ).strip()

        if headline:
            normalized_variants.append(
                {
                    "type": social_proof_type,
                    "headline": headline,
                }
            )

    profile[
        "social_proof_variants"
    ] = normalized_variants


def select_social_proof_variant(
    social_proof_variants: list[dict],
    conversion_strategy: str | None = None,
) -> dict:

    strategy = normalize_social_proof_type(
        conversion_strategy
    )

    preferred_order = (
        SOCIAL_PROOF_STRATEGY_MAP.get(
            strategy,
            SOCIAL_PROOF_STRATEGY_MAP[
                "general"
            ],
        )
    )

    normalized_variants = []

    for variant in (
        social_proof_variants or []
    ):

        if not isinstance(
            variant,
            dict,
        ):
            continue

        social_proof_type = (
            normalize_social_proof_type(
                variant.get("type")
            )
        )

        headline = str(
            variant.get(
                "headline",
                "",
            )
        ).strip()

        if not headline:
            continue

        normalized_variants.append(
            {
                **variant,
                "type": social_proof_type,
                "headline": headline,
            }
        )

    for preferred_type in preferred_order:

        for variant in normalized_variants:

            if (
                variant["type"]
                == preferred_type
            ):
                return variant

    for fallback_type in (
        SOCIAL_PROOF_FALLBACK_ORDER
    ):

        for variant in normalized_variants:

            if (
                variant["type"]
                == fallback_type
            ):
                return variant

    return {
        "type": "customers",
        "headline": (
            "Trusted by Customers"
        ),
    }
