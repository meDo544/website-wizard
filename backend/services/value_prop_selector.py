from typing import Any


VALUE_PROP_STRATEGY_MAP = {
    "restaurant": [
        "quality",
        "convenience",
        "cost_savings",
    ],
    "saas": [
        "speed",
        "innovation",
        "cost_savings",
    ],
    "consultant": [
        "expertise",
        "results",
        "reliability",
    ],
    "contractor": [
        "reliability",
        "quality",
        "cost_savings",
    ],
    "agency": [
        "results",
        "innovation",
        "expertise",
    ],
    "medical": [
        "expertise",
        "reliability",
        "quality",
    ],
    "general": [
        "quality",
    ],
}


VALUE_PROP_FALLBACK_ORDER = [
    "quality",
    "speed",
    "cost_savings",
    "innovation",
    "expertise",
    "convenience",
    "reliability",
    "results",
    "general",
]


VALUE_PROP_TYPE_ALIASES = {
    "fast": "speed",
    "faster": "speed",
    "save_money": "cost_savings",
    "affordable": "cost_savings",
    "cutting_edge": "innovation",
    "advanced": "innovation",
    "professional": "expertise",
    "specialist": "expertise",
    "easy": "convenience",
    "trusted": "reliability",
    "dependable": "reliability",
    "outcomes": "results",
}


def normalize_value_prop_type(
    value_prop_type: str | None,
) -> str:

    if not value_prop_type:
        return "general"

    normalized = (
        str(value_prop_type)
        .strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )

    return VALUE_PROP_TYPE_ALIASES.get(
        normalized,
        normalized,
    )


def _normalize_value_prop_variants(
    profile: dict[str, Any],
) -> None:

    variants = profile.get(
        "value_prop_variants",
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

        value_prop_type = (
            normalize_value_prop_type(
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
                    "type": value_prop_type,
                    "headline": headline,
                }
            )

    profile[
        "value_prop_variants"
    ] = normalized_variants


def select_value_prop_variant(
    value_prop_variants: list[dict],
    conversion_strategy: str | None = None,
) -> dict:

    strategy = normalize_value_prop_type(
        conversion_strategy
    )

    preferred_order = (
        VALUE_PROP_STRATEGY_MAP.get(
            strategy,
            VALUE_PROP_STRATEGY_MAP[
                "general"
            ],
        )
    )

    normalized_variants = []

    for variant in (
        value_prop_variants or []
    ):

        if not isinstance(
            variant,
            dict,
        ):
            continue

        value_prop_type = (
            normalize_value_prop_type(
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
                "type": value_prop_type,
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
        VALUE_PROP_FALLBACK_ORDER
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
            "Premium Quality You Can Trust"
        ),
    }
