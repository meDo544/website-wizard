from typing import Any


BUYER_MOTIVATION_STRATEGY_MAP = {
    "restaurant": [
        "comfort",
        "save_money",
        "status",
    ],
    "saas": [
        "save_time",
        "growth",
        "success",
    ],
    "consultant": [
        "growth",
        "success",
        "security",
    ],
    "contractor": [
        "security",
        "save_money",
        "comfort",
    ],
    "agency": [
        "growth",
        "status",
        "success",
    ],
    "medical": [
        "security",
        "comfort",
        "save_time",
    ],
    "general": ["growth"],
}


BUYER_MOTIVATION_FALLBACK_ORDER = [
    "growth",
    "save_time",
    "save_money",
    "success",
    "comfort",
    "security",
    "status",
    "general",
]


BUYER_MOTIVATION_TYPE_ALIASES = {
    "time_savings": "save_time",
    "money_savings": "save_money",
    "wealth": "save_money",
    "achievement": "success",
    "winning": "success",
    "safety": "security",
    "safe": "security",
    "ease": "comfort",
    "convenience": "comfort",
    "scale": "growth",
}


def normalize_buyer_motivation_type(
    buyer_motivation_type: str | None,
) -> str:
    if not buyer_motivation_type:
        return "general"

    normalized = (
        str(buyer_motivation_type)
        .strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )

    return BUYER_MOTIVATION_TYPE_ALIASES.get(
        normalized,
        normalized,
    )


def _normalize_buyer_motivation_variants(
    profile: dict[str, Any],
) -> None:
    variants = profile.get(
        "buyer_motivation_variants",
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

        buyer_motivation_type = (
            normalize_buyer_motivation_type(
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
                    "type": buyer_motivation_type,
                    "headline": headline,
                }
            )

    profile[
        "buyer_motivation_variants"
    ] = normalized_variants


def select_buyer_motivation_variant(
    buyer_motivation_variants: list[dict],
    conversion_strategy: str | None = None,
) -> dict:
    strategy = normalize_buyer_motivation_type(
        conversion_strategy
    )

    preferred_order = (
        BUYER_MOTIVATION_STRATEGY_MAP.get(
            strategy,
            BUYER_MOTIVATION_STRATEGY_MAP[
                "general"
            ],
        )
    )

    normalized_variants = []

    for variant in (
        buyer_motivation_variants or []
    ):
        if not isinstance(
            variant,
            dict,
        ):
            continue

        buyer_motivation_type = (
            normalize_buyer_motivation_type(
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
                "type": buyer_motivation_type,
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
        BUYER_MOTIVATION_FALLBACK_ORDER
    ):
        for variant in normalized_variants:
            if (
                variant["type"]
                == fallback_type
            ):
                return variant

    return {
        "type": "growth",
        "headline": (
            "Accelerate Your Personal and Business Growth"
        ),
    }
