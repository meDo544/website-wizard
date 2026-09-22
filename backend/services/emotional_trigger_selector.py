from typing import Any


EMOTIONAL_TRIGGER_STRATEGY_MAP = {
    "restaurant": [
        "belonging",
        "aspiration",
        "confidence",
    ],
    "saas": [
        "achievement",
        "aspiration",
        "confidence",
    ],
    "consultant": [
        "confidence",
        "security",
        "achievement",
    ],
    "contractor": [
        "security",
        "confidence",
        "belonging",
    ],
    "agency": [
        "aspiration",
        "achievement",
        "status",
    ],
    "medical": [
        "security",
        "confidence",
        "belonging",
    ],
    "general": ["aspiration"],
}


EMOTIONAL_TRIGGER_FALLBACK_ORDER = [
    "aspiration",
    "security",
    "confidence",
    "achievement",
    "status",
    "belonging",
    "fear_of_missing_out",
    "general",
]


EMOTIONAL_TRIGGER_TYPE_ALIASES = {
    "fomo": "fear_of_missing_out",
    "trust": "confidence",
    "safe": "security",
    "safety": "security",
    "success": "achievement",
    "winning": "achievement",
    "prestige": "status",
    "community": "belonging",
    "dream": "aspiration",
}


def normalize_emotional_trigger_type(
    emotional_trigger_type: str | None,
) -> str:
    if not emotional_trigger_type:
        return "general"

    normalized = (
        str(emotional_trigger_type)
        .strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )

    return EMOTIONAL_TRIGGER_TYPE_ALIASES.get(
        normalized,
        normalized,
    )


def _normalize_emotional_trigger_variants(
    profile: dict[str, Any],
) -> None:
    variants = profile.get(
        "emotional_trigger_variants",
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

        emotional_trigger_type = (
            normalize_emotional_trigger_type(
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
                    "type": emotional_trigger_type,
                    "headline": headline,
                }
            )

    profile[
        "emotional_trigger_variants"
    ] = normalized_variants


def select_emotional_trigger_variant(
    emotional_trigger_variants: list[dict],
    conversion_strategy: str | None = None,
) -> dict:
    strategy = normalize_emotional_trigger_type(
        conversion_strategy
    )

    preferred_order = (
        EMOTIONAL_TRIGGER_STRATEGY_MAP.get(
            strategy,
            EMOTIONAL_TRIGGER_STRATEGY_MAP[
                "general"
            ],
        )
    )

    normalized_variants = []

    for variant in (
        emotional_trigger_variants or []
    ):
        if not isinstance(
            variant,
            dict,
        ):
            continue

        emotional_trigger_type = (
            normalize_emotional_trigger_type(
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
                "type": emotional_trigger_type,
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
        EMOTIONAL_TRIGGER_FALLBACK_ORDER
    ):
        for variant in normalized_variants:
            if (
                variant["type"]
                == fallback_type
            ):
                return variant

    return {
        "type": "aspiration",
        "headline": (
            "Achieve More With Less Effort"
        ),
    }
