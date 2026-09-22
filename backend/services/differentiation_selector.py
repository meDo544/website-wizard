from typing import Any


DIFFERENTIATION_STRATEGY_MAP = {
    "restaurant": [
        "quality",
        "service",
        "customization",
    ],
    "saas": [
        "innovation",
        "speed",
        "customization",
    ],
    "consultant": [
        "expertise",
        "service",
        "customization",
    ],
    "contractor": [
        "quality",
        "service",
        "price",
    ],
    "agency": [
        "innovation",
        "expertise",
        "customization",
    ],
    "medical": [
        "expertise",
        "quality",
        "service",
    ],
    "general": [
        "quality",
    ],
}


DIFFERENTIATION_FALLBACK_ORDER = [
    "quality",
    "innovation",
    "service",
    "expertise",
    "speed",
    "price",
    "customization",
    "general",
]


DIFFERENTIATION_TYPE_ALIASES = {
    "premium": "quality",
    "advanced": "innovation",
    "technology": "innovation",
    "support": "service",
    "customer_service": "service",
    "specialist": "expertise",
    "professional": "expertise",
    "fast": "speed",
    "affordable": "price",
    "personalized": "customization",
    "tailored": "customization",
}


def normalize_differentiation_type(
    differentiation_type: str | None,
) -> str:
    if not differentiation_type:
        return "general"

    normalized = (
        str(differentiation_type)
        .strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )

    return DIFFERENTIATION_TYPE_ALIASES.get(
        normalized,
        normalized,
    )


def _normalize_differentiation_variants(
    profile: dict[str, Any],
) -> None:
    variants = profile.get(
        "differentiation_variants",
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

        differentiation_type = (
            normalize_differentiation_type(
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
                    "type": differentiation_type,
                    "headline": headline,
                }
            )

    profile[
        "differentiation_variants"
    ] = normalized_variants


def select_differentiation_variant(
    differentiation_variants: list[dict],
    conversion_strategy: str | None = None,
) -> dict:
    strategy = normalize_differentiation_type(
        conversion_strategy
    )

    preferred_order = (
        DIFFERENTIATION_STRATEGY_MAP.get(
            strategy,
            DIFFERENTIATION_STRATEGY_MAP[
                "general"
            ],
        )
    )

    normalized_variants = []

    for variant in (
        differentiation_variants or []
    ):
        if not isinstance(
            variant,
            dict,
        ):
            continue

        differentiation_type = (
            normalize_differentiation_type(
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
                "type": differentiation_type,
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
        DIFFERENTIATION_FALLBACK_ORDER
    ):
        for variant in normalized_variants:
            if (
                variant["type"]
                == fallback_type
            ):
                return variant

    return {
        "type": "quality",
        "headline": (
            "Higher Quality Than Typical Alternatives"
        ),
    }
