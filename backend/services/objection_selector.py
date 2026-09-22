from typing import Any


OBJECTION_STRATEGY_MAP = {
    "restaurant": [
        "price",
        "trust",
        "convenience",
    ],
    "saas": [
        "complexity",
        "price",
        "trust",
    ],
    "consultant": [
        "trust",
        "price",
        "results",
    ],
    "contractor": [
        "trust",
        "price",
        "timeline",
    ],
    "agency": [
        "results",
        "price",
        "trust",
    ],
    "medical": [
        "trust",
        "safety",
        "convenience",
    ],
    "general": [
        "trust",
    ],
}


OBJECTION_FALLBACK_ORDER = [
    "trust",
    "price",
    "complexity",
    "results",
    "timeline",
    "safety",
    "convenience",
    "general",
]


OBJECTION_TYPE_ALIASES = {
    "cost": "price",
    "budget": "price",
    "expensive": "price",
    "difficulty": "complexity",
    "hard_to_use": "complexity",
    "setup": "complexity",
    "credibility": "trust",
    "proof": "results",
    "speed": "timeline",
    "time": "timeline",
    "risk": "safety",
    "easy": "convenience",
}


def normalize_objection_type(
    objection_type: str | None,
) -> str:

    if not objection_type:
        return "general"

    normalized = (
        str(objection_type)
        .strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )

    return OBJECTION_TYPE_ALIASES.get(
        normalized,
        normalized,
    )


def _normalize_objection_variants(
    profile: dict[str, Any],
) -> None:

    variants = profile.get(
        "objection_variants",
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

        objection_type = (
            normalize_objection_type(
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
                    "type": objection_type,
                    "headline": headline,
                }
            )

    profile[
        "objection_variants"
    ] = normalized_variants


def select_objection_variant(
    objection_variants: list[dict],
    conversion_strategy: str | None = None,
) -> dict:

    strategy = normalize_objection_type(
        conversion_strategy
    )

    preferred_order = (
        OBJECTION_STRATEGY_MAP.get(
            strategy,
            OBJECTION_STRATEGY_MAP[
                "general"
            ],
        )
    )

    normalized_variants = []

    for variant in (
        objection_variants or []
    ):

        if not isinstance(
            variant,
            dict,
        ):
            continue

        objection_type = (
            normalize_objection_type(
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
                "type": objection_type,
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
        OBJECTION_FALLBACK_ORDER
    ):

        for variant in normalized_variants:

            if (
                variant["type"]
                == fallback_type
            ):
                return variant

    return {
        "type": "trust",
        "headline": (
            "Trusted Support Every Step of the Way"
        ),
    }
