from typing import Any


OUTCOME_STRATEGY_MAP = {
    "restaurant": [
        "simplicity",
        "freedom",
        "confidence",
    ],
    "saas": [
        "efficiency",
        "growth",
        "speed",
    ],
    "consultant": [
        "growth",
        "confidence",
        "profitability",
    ],
    "contractor": [
        "simplicity",
        "confidence",
        "freedom",
    ],
    "agency": [
        "growth",
        "profitability",
        "speed",
    ],
    "medical": [
        "confidence",
        "freedom",
        "simplicity",
    ],
    "general": [
        "growth",
    ],
}


OUTCOME_FALLBACK_ORDER = [
    "growth",
    "efficiency",
    "freedom",
    "confidence",
    "profitability",
    "simplicity",
    "speed",
    "general",
]


OUTCOME_TYPE_ALIASES = {
    "scale": "growth",
    "scaling": "growth",
    "productivity": "efficiency",
    "performance": "efficiency",
    "independence": "freedom",
    "peace_of_mind": "freedom",
    "certainty": "confidence",
    "assurance": "confidence",
    "revenue": "profitability",
    "income": "profitability",
    "easy": "simplicity",
    "ease": "simplicity",
    "fast": "speed",
    "quick": "speed",
}


def normalize_outcome_type(
    outcome_type: str | None,
) -> str:
    if not outcome_type:
        return "general"

    normalized = (
        str(outcome_type)
        .strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )

    return OUTCOME_TYPE_ALIASES.get(
        normalized,
        normalized,
    )


def _normalize_outcome_variants(
    profile: dict[str, Any],
) -> None:
    variants = profile.get(
        "outcome_variants",
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

        outcome_type = (
            normalize_outcome_type(
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
                    "type": outcome_type,
                    "headline": headline,
                }
            )

    profile[
        "outcome_variants"
    ] = normalized_variants


def select_outcome_variant(
    outcome_variants: list[dict],
    conversion_strategy: str | None = None,
) -> dict:
    strategy = normalize_outcome_type(
        conversion_strategy
    )

    preferred_order = (
        OUTCOME_STRATEGY_MAP.get(
            strategy,
            OUTCOME_STRATEGY_MAP[
                "general"
            ],
        )
    )

    normalized_variants = []

    for variant in (
        outcome_variants or []
    ):
        if not isinstance(
            variant,
            dict,
        ):
            continue

        outcome_type = (
            normalize_outcome_type(
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
                "type": outcome_type,
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
        OUTCOME_FALLBACK_ORDER
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
            "Accelerate Your Business Growth"
        ),
    }
