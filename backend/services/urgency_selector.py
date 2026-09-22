from typing import Any


URGENCY_STRATEGY_MAP = {
    "restaurant": [
        "limited_time",
        "seasonal",
        "limited_stock",
    ],
    "saas": [
        "limited_time",
        "expiring_bonus",
        "limited_access",
    ],
    "consultant": [
        "limited_time",
        "limited_spots",
        "expiring_bonus",
    ],
    "contractor": [
        "seasonal",
        "limited_time",
        "limited_spots",
    ],
    "agency": [
        "limited_spots",
        "limited_time",
        "expiring_bonus",
    ],
    "medical": [
        "limited_spots",
        "seasonal",
        "limited_time",
    ],
    "general": [
        "limited_time",
    ],
}


URGENCY_FALLBACK_ORDER = [
    "limited_time",
    "limited_spots",
    "limited_stock",
    "seasonal",
    "expiring_bonus",
    "limited_access",
    "general",
]


URGENCY_TYPE_ALIASES = {
    "deadline": "limited_time",
    "countdown": "limited_time",
    "spots": "limited_spots",
    "availability": "limited_spots",
    "stock": "limited_stock",
    "inventory": "limited_stock",
    "bonus_expiry": "expiring_bonus",
    "early_access": "limited_access",
}


def normalize_urgency_type(
    urgency_type: str | None,
) -> str:

    if not urgency_type:
        return "general"

    normalized = (
        str(urgency_type)
        .strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )

    return URGENCY_TYPE_ALIASES.get(
        normalized,
        normalized,
    )


def _normalize_urgency_variants(
    profile: dict[str, Any],
) -> None:

    variants = profile.get(
        "urgency_variants",
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

        urgency_type = (
            normalize_urgency_type(
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
                    "type": urgency_type,
                    "headline": headline,
                }
            )

    profile[
        "urgency_variants"
    ] = normalized_variants


def select_urgency_variant(
    urgency_variants: list[dict],
    conversion_strategy: str | None = None,
) -> dict:

    strategy = normalize_urgency_type(
        conversion_strategy
    )

    preferred_order = (
        URGENCY_STRATEGY_MAP.get(
            strategy,
            URGENCY_STRATEGY_MAP[
                "general"
            ],
        )
    )

    normalized_variants = []

    for variant in (
        urgency_variants or []
    ):

        if not isinstance(
            variant,
            dict,
        ):
            continue

        urgency_type = (
            normalize_urgency_type(
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
                "type": urgency_type,
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
        URGENCY_FALLBACK_ORDER
    ):

        for variant in normalized_variants:

            if (
                variant["type"]
                == fallback_type
            ):
                return variant

    return {
        "type": "limited_time",
        "headline": (
            "Limited Time Offer Available"
        ),
    }
