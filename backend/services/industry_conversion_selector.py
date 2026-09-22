from typing import Any


INDUSTRY_CONVERSION_STRATEGY_MAP = {
    "restaurant": ["restaurant", "local", "consumer"],
    "saas": ["saas", "technology", "business"],
    "consultant": ["consultant", "professional", "business"],
    "contractor": ["contractor", "local", "trust"],
    "agency": ["agency", "creative", "business"],
    "medical": ["medical", "trust", "local"],
    "general": ["general"],
}

INDUSTRY_CONVERSION_FALLBACK_ORDER = [
    "restaurant",
    "saas",
    "consultant",
    "contractor",
    "agency",
    "medical",
    "ecommerce",
    "technology",
    "professional",
    "business",
    "creative",
    "local",
    "consumer",
    "trust",
    "general",
]

INDUSTRY_CONVERSION_TYPE_ALIASES = {
    "software": "saas",
    "tech": "technology",
    "online_store": "ecommerce",
    "shop": "ecommerce",
    "retail": "ecommerce",
    "service_business": "professional",
    "small_business": "business",
    "nearby": "local",
    "community": "local",
    "customer": "consumer",
    "credibility": "trust",
}


def normalize_industry_conversion_type(
    industry_conversion_type: str | None,
) -> str:
    if not industry_conversion_type:
        return "general"

    normalized = (
        str(industry_conversion_type)
        .strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )

    return INDUSTRY_CONVERSION_TYPE_ALIASES.get(
        normalized,
        normalized,
    )


def _normalize_industry_conversion_variants(
    profile: dict[str, Any],
) -> None:
    variants = profile.get(
        "industry_conversion_variants",
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

        industry_type = (
            normalize_industry_conversion_type(
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
                    "type": industry_type,
                    "headline": headline,
                }
            )

    profile[
        "industry_conversion_variants"
    ] = normalized_variants


def select_industry_conversion_variant(
    industry_conversion_variants: list[dict],
    conversion_strategy: str | None = None,
) -> dict:
    strategy = (
        normalize_industry_conversion_type(
            conversion_strategy
        )
    )

    preferred_order = (
        INDUSTRY_CONVERSION_STRATEGY_MAP.get(
            strategy,
            INDUSTRY_CONVERSION_STRATEGY_MAP[
                "general"
            ],
        )
    )

    normalized_variants = []

    for variant in (
        industry_conversion_variants or []
    ):
        if not isinstance(
            variant,
            dict,
        ):
            continue

        industry_type = (
            normalize_industry_conversion_type(
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
                "type": industry_type,
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
        INDUSTRY_CONVERSION_FALLBACK_ORDER
    ):
        for variant in normalized_variants:
            if (
                variant["type"]
                == fallback_type
            ):
                return variant

    return {
        "type": "general",
        "headline": (
            "Optimized for High-Converting Businesses"
        ),
    }
