from typing import Any


RISK_REVERSAL_STRATEGY_MAP = {
    "restaurant": ["guarantee", "bonus", "general"],
    "saas": ["free_trial", "money_back", "guarantee"],
    "consultant": ["consultation", "guarantee", "bonus"],
    "contractor": ["guarantee", "warranty", "money_back"],
    "agency": ["guarantee", "consultation", "money_back"],
    "medical": ["guarantee", "consultation", "general"],
    "general": ["guarantee"],
}


RISK_REVERSAL_FALLBACK_ORDER = [
    "guarantee",
    "money_back",
    "free_trial",
    "warranty",
    "consultation",
    "bonus",
    "general",
]


RISK_REVERSAL_TYPE_ALIASES = {
    "moneyback": "money_back",
    "money_back_guarantee": "money_back",
    "trial": "free_trial",
    "free_trial_offer": "free_trial",
    "warranty_offer": "warranty",
    "free_consultation": "consultation",
}


def normalize_risk_reversal_type(
    risk_reversal_type: str | None,
) -> str:

    if not risk_reversal_type:
        return "general"

    normalized = (
        str(risk_reversal_type)
        .strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )

    return RISK_REVERSAL_TYPE_ALIASES.get(
        normalized,
        normalized,
    )


def _normalize_risk_reversal_variants(
    profile: dict[str, Any],
) -> None:

    variants = profile.get(
        "risk_reversal_variants",
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

        risk_reversal_type = (
            normalize_risk_reversal_type(
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
                    "type": risk_reversal_type,
                    "headline": headline,
                }
            )

    profile[
        "risk_reversal_variants"
    ] = normalized_variants


def select_risk_reversal_variant(
    risk_reversal_variants: list[dict],
    conversion_strategy: str | None = None,
) -> dict:

    strategy = normalize_risk_reversal_type(
        conversion_strategy
    )

    preferred_order = (
        RISK_REVERSAL_STRATEGY_MAP.get(
            strategy,
            RISK_REVERSAL_STRATEGY_MAP[
                "general"
            ],
        )
    )

    normalized_variants = []

    for variant in (
        risk_reversal_variants or []
    ):

        if not isinstance(
            variant,
            dict,
        ):
            continue

        risk_reversal_type = (
            normalize_risk_reversal_type(
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
                "type": risk_reversal_type,
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
        RISK_REVERSAL_FALLBACK_ORDER
    ):

        for variant in normalized_variants:

            if (
                variant["type"]
                == fallback_type
            ):
                return variant

    return {
        "type": "guarantee",
        "headline": (
            "100% Satisfaction Guaranteed"
        ),
    }
