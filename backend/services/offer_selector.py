from typing import Any


OFFER_STRATEGY_MAP = {
    "restaurant": ["discount", "bonus"],
    "saas": ["trial", "demo"],
    "consultant": ["consultation", "audit"],
    "contractor": ["quote", "discount"],
    "agency": ["consultation", "audit"],
    "medical": ["appointment", "consultation"],
    "general": ["discount"],
}

OFFER_FALLBACK_ORDER = [
    "consultation",
    "audit",
    "discount",
    "trial",
    "demo",
    "quote",
    "bonus",
    "appointment",
    "general",
]

OFFER_TYPE_ALIASES = {
    "free_consultation": "consultation",
    "consult": "consultation",
    "strategy_session": "consultation",
    "assessment": "audit",
    "review": "audit",
    "sale": "discount",
    "coupon": "discount",
    "promo": "discount",
}


def normalize_offer_type(offer_type: str | None) -> str:
    if not offer_type:
        return "general"

    normalized = (
        str(offer_type)
        .strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )

    return OFFER_TYPE_ALIASES.get(normalized, normalized)


def _normalize_offer_variants(
    profile: dict[str, Any],
) -> None:
    variants = profile.get(
        "offer_variants",
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

        offer_type = normalize_offer_type(
            variant.get("type")
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
                    **variant,
                    "type": offer_type,
                    "headline": headline,
                }
            )

    profile["offer_variants"] = normalized_variants


def select_offer_variant(
    offer_variants: list[dict[str, Any]],
    conversion_strategy: str | None = None,
) -> dict[str, Any]:

    strategy = normalize_offer_type(
        conversion_strategy
    )

    preferred_order = OFFER_STRATEGY_MAP.get(
        strategy,
        OFFER_STRATEGY_MAP["general"],
    )

    normalized_variants = []

    for variant in offer_variants or []:

        if not isinstance(
            variant,
            dict,
        ):
            continue

        offer_type = normalize_offer_type(
            variant.get("type")
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
                "type": offer_type,
                "headline": headline,
            }
        )

    for preferred_type in preferred_order:

        for variant in normalized_variants:

            if variant["type"] == preferred_type:
                return variant

    for fallback_type in OFFER_FALLBACK_ORDER:

        for variant in normalized_variants:

            if variant["type"] == fallback_type:
                return variant

    return {
        "type": "discount",
        "headline": "Special Offer Available Today",
    }
