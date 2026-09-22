from typing import Any


AUTHORITY_STRATEGY_MAP = {
    "restaurant": ["experience", "credibility", "results"],
    "saas": ["expertise", "innovation", "results"],
    "consultant": ["expertise", "leadership", "results"],
    "contractor": ["experience", "certification", "credibility"],
    "agency": ["results", "leadership", "innovation"],
    "medical": ["certification", "expertise", "credibility"],
    "general": ["expertise"],
}

AUTHORITY_FALLBACK_ORDER = [
    "expertise",
    "experience",
    "certification",
    "results",
    "leadership",
    "innovation",
    "credibility",
    "general",
]

AUTHORITY_TYPE_ALIASES = {
    "expert": "expertise",
    "specialist": "expertise",
    "years": "experience",
    "track_record": "experience",
    "licensed": "certification",
    "accredited": "certification",
    "success": "results",
    "performance": "results",
    "visionary": "leadership",
    "industry_leader": "leadership",
    "technology": "innovation",
    "cutting_edge": "innovation",
    "trusted": "credibility",
    "reputation": "credibility",
}


def normalize_authority_type(
    authority_type: str | None,
) -> str:
    if not authority_type:
        return "general"

    normalized = (
        str(authority_type)
        .strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )

    return AUTHORITY_TYPE_ALIASES.get(
        normalized,
        normalized,
    )


def _normalize_authority_variants(
    profile: dict[str, Any],
) -> None:
    variants = profile.get(
        "authority_variants",
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

        authority_type = (
            normalize_authority_type(
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
                    "type": authority_type,
                    "headline": headline,
                }
            )

    profile[
        "authority_variants"
    ] = normalized_variants


def select_authority_variant(
    authority_variants: list[dict],
    conversion_strategy: str | None = None,
) -> dict:
    strategy = normalize_authority_type(
        conversion_strategy
    )

    preferred_order = (
        AUTHORITY_STRATEGY_MAP.get(
            strategy,
            AUTHORITY_STRATEGY_MAP[
                "general"
            ],
        )
    )

    normalized_variants = []

    for variant in (
        authority_variants or []
    ):
        if not isinstance(
            variant,
            dict,
        ):
            continue

        authority_type = (
            normalize_authority_type(
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
                "type": authority_type,
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
        AUTHORITY_FALLBACK_ORDER
    ):
        for variant in normalized_variants:
            if (
                variant["type"]
                == fallback_type
            ):
                return variant

    return {
        "type": "expertise",
        "headline": (
            "Trusted Experts in Your Industry"
        ),
    }
