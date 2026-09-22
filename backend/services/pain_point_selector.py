from typing import Any


PAIN_POINT_STRATEGY_MAP = {
    "restaurant": [
        "time",
        "frustration",
        "cost",
    ],
    "saas": [
        "time",
        "complexity",
        "competition",
    ],
    "consultant": [
        "uncertainty",
        "risk",
        "competition",
    ],
    "contractor": [
        "risk",
        "cost",
        "time",
    ],
    "agency": [
        "competition",
        "complexity",
        "time",
    ],
    "medical": [
        "risk",
        "uncertainty",
        "time",
    ],
    "general": ["time"],
}


PAIN_POINT_FALLBACK_ORDER = [
    "time",
    "cost",
    "complexity",
    "risk",
    "frustration",
    "competition",
    "uncertainty",
    "general",
]


PAIN_POINT_TYPE_ALIASES = {
    "expense": "cost",
    "pricing": "cost",
    "slow": "time",
    "delay": "time",
    "confusion": "complexity",
    "difficult": "complexity",
    "danger": "risk",
    "mistakes": "risk",
    "stress": "frustration",
    "overwhelm": "frustration",
    "rivalry": "competition",
    "unknown": "uncertainty",
}


def normalize_pain_point_type(
    pain_point_type: str | None,
) -> str:
    if not pain_point_type:
        return "general"

    normalized = (
        str(pain_point_type)
        .strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )

    return PAIN_POINT_TYPE_ALIASES.get(
        normalized,
        normalized,
    )


def _normalize_pain_point_variants(
    profile: dict[str, Any],
) -> None:
    variants = profile.get(
        "pain_point_variants",
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

        pain_point_type = (
            normalize_pain_point_type(
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
                    "type": pain_point_type,
                    "headline": headline,
                }
            )

    profile[
        "pain_point_variants"
    ] = normalized_variants


def select_pain_point_variant(
    pain_point_variants: list[dict],
    conversion_strategy: str | None = None,
) -> dict:
    strategy = normalize_pain_point_type(
        conversion_strategy
    )

    preferred_order = (
        PAIN_POINT_STRATEGY_MAP.get(
            strategy,
            PAIN_POINT_STRATEGY_MAP[
                "general"
            ],
        )
    )

    normalized_variants = []

    for variant in (
        pain_point_variants or []
    ):
        if not isinstance(
            variant,
            dict,
        ):
            continue

        pain_point_type = (
            normalize_pain_point_type(
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
                "type": pain_point_type,
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
        PAIN_POINT_FALLBACK_ORDER
    ):
        for variant in normalized_variants:
            if (
                variant["type"]
                == fallback_type
            ):
                return variant

    return {
        "type": "time",
        "headline": (
            "Stop Wasting Time on Outdated Solutions"
        ),
    }
