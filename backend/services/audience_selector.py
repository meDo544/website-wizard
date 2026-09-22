from typing import Any


AUDIENCE_STRATEGY_MAP = {
    "restaurant": [
        "consumer",
        "premium",
        "beginner",
    ],
    "saas": [
        "professional",
        "enterprise",
        "small_business",
    ],
    "consultant": [
        "professional",
        "small_business",
        "premium",
    ],
    "contractor": [
        "consumer",
        "small_business",
        "premium",
    ],
    "agency": [
        "small_business",
        "enterprise",
        "professional",
    ],
    "medical": [
        "consumer",
        "premium",
        "professional",
    ],
    "general": [
        "consumer",
    ],
}


AUDIENCE_FALLBACK_ORDER = [
    "consumer",
    "professional",
    "small_business",
    "enterprise",
    "premium",
    "beginner",
    "general",
]


AUDIENCE_TYPE_ALIASES = {
    "starter": "beginner",
    "newbie": "beginner",
    "business": "small_business",
    "smb": "small_business",
    "corporate": "enterprise",
    "company": "enterprise",
    "expert": "professional",
    "pro": "professional",
    "luxury": "premium",
    "high_end": "premium",
}


def normalize_audience_type(
    audience_type: str | None,
) -> str:

    if not audience_type:
        return "general"

    normalized = (
        str(audience_type)
        .strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )

    return AUDIENCE_TYPE_ALIASES.get(
        normalized,
        normalized,
    )


def _normalize_audience_variants(
    profile: dict[str, Any],
) -> None:

    variants = profile.get(
        "audience_variants",
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

        audience_type = (
            normalize_audience_type(
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
                    "type": audience_type,
                    "headline": headline,
                }
            )

    profile[
        "audience_variants"
    ] = normalized_variants


def select_audience_variant(
    audience_variants: list[dict],
    conversion_strategy: str | None = None,
) -> dict:

    strategy = normalize_audience_type(
        conversion_strategy
    )

    preferred_order = (
        AUDIENCE_STRATEGY_MAP.get(
            strategy,
            AUDIENCE_STRATEGY_MAP[
                "general"
            ],
        )
    )

    normalized_variants = []

    for variant in (
        audience_variants or []
    ):

        if not isinstance(
            variant,
            dict,
        ):
            continue

        audience_type = (
            normalize_audience_type(
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
                "type": audience_type,
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
        AUDIENCE_FALLBACK_ORDER
    ):

        for variant in normalized_variants:

            if (
                variant["type"]
                == fallback_type
            ):
                return variant

    return {
        "type": "consumer",
        "headline": (
            "Designed for Everyday Customers"
        ),
    }
