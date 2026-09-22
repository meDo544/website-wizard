from typing import Any


TRUST_STRATEGY_MAP = {
    "restaurant": ["reviews", "local", "guarantee"],
    "saas": ["security", "customers", "case_study"],
    "consultant": ["experience", "authority", "results"],
    "contractor": ["reviews", "licensed", "guarantee"],
    "agency": ["case_study", "results", "clients"],
    "medical": ["certification", "reviews", "experience"],
    "general": ["reviews"],
}


TRUST_FALLBACK_ORDER = [
    "reviews",
    "experience",
    "guarantee",
    "authority",
    "results",
    "case_study",
    "clients",
    "customers",
    "security",
    "licensed",
    "certification",
    "local",
    "general",
]


TRUST_TYPE_ALIASES = {
    "testimonial": "reviews",
    "testimonials": "reviews",
    "rating": "reviews",
    "ratings": "reviews",
    "years": "experience",
    "years_in_business": "experience",
    "proof": "results",
    "portfolio": "case_study",
    "certified": "certification",
    "licensed_insured": "licensed",
}


def normalize_trust_type(
    trust_type: str | None,
) -> str:
    if not trust_type:
        return "general"

    normalized = (
        str(trust_type)
        .strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )

    return TRUST_TYPE_ALIASES.get(
        normalized,
        normalized,
    )


def _normalize_trust_variants(
    profile: dict[str, Any],
) -> None:
    variants = profile.get(
        "trust_variants",
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

        trust_type = normalize_trust_type(
            variant.get("type")
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
                    "type": trust_type,
                    "headline": headline,
                }
            )

    profile["trust_variants"] = normalized_variants


def select_trust_variant(
    trust_variants: list[dict],
    conversion_strategy: str | None = None,
) -> dict:
    strategy = normalize_trust_type(
        conversion_strategy
    )

    preferred_order = TRUST_STRATEGY_MAP.get(
        strategy,
        TRUST_STRATEGY_MAP["general"],
    )

    normalized_variants = []

    for variant in trust_variants or []:
        if not isinstance(
            variant,
            dict,
        ):
            continue

        trust_type = normalize_trust_type(
            variant.get("type")
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
                "type": trust_type,
                "headline": headline,
            }
        )

    for preferred_type in preferred_order:
        for variant in normalized_variants:
            if variant["type"] == preferred_type:
                return variant

    for fallback_type in TRUST_FALLBACK_ORDER:
        for variant in normalized_variants:
            if variant["type"] == fallback_type:
                return variant

    return {
        "type": "discount",
        "headline": "Special Trust Available Today",
    }
