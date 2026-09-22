from typing import Any

from backend.domain.website_state import WebsiteState


CTA_STRATEGY_MAP = {
    "restaurant": ["booking", "purchase"],
    "saas": ["demo", "trial"],
    "consultant": ["consultation", "booking"],
    "contractor": ["quote", "booking"],
    "agency": ["consultation", "quote"],
    "medical": ["appointment", "booking"],
    "general": ["booking"],
}

CTA_FALLBACK_ORDER = [
    "booking",
    "consultation",
    "quote",
    "demo",
    "trial",
    "purchase",
    "appointment",
    "general",
]

CTA_TYPE_ALIASES = {
    "book": "booking",
    "reservation": "booking",
    "reserve": "booking",
    "call": "consultation",
    "consult": "consultation",
    "estimate": "quote",
    "pricing": "quote",
    "buy": "purchase",
    "order": "purchase",
    "signup": "trial",
    "sign_up": "trial",
    "free_trial": "trial",
    "schedule": "appointment",
}

def normalize_cta_type(cta_type: str | None) -> str:
    if not cta_type:
        return "general"

    normalized = str(cta_type).strip().lower().replace("-", "_").replace(" ", "_")
    return CTA_TYPE_ALIASES.get(normalized, normalized)

def _normalize_cta_variants(
    profile: dict[str, Any],
) -> None:
    variants = profile.get("cta_variants", [])

    if not isinstance(variants, list):
        variants = []

    normalized_variants = []

    for variant in variants:
        if not isinstance(variant, dict):
            continue

        cta_type = normalize_cta_type(
            variant.get("type")
        )

        text = str(
            variant.get("text", "")
        ).strip()

        if text:
            normalized_variants.append(
                {
                    "type": cta_type,
                    "text": text,
                }
            )

    profile["cta_variants"] = normalized_variants

def select_cta_variant(
    cta_variants: list[dict],
    conversion_strategy: str | None = None,
) -> dict:
    strategy = normalize_cta_type(conversion_strategy)

    preferred_order = CTA_STRATEGY_MAP.get(
        strategy,
        CTA_STRATEGY_MAP["general"],
    )

    normalized_variants = []

    for variant in cta_variants or []:
        if not isinstance(variant, dict):
            continue

        variant_type = normalize_cta_type(
            variant.get("type")
        )

        text = str(
            variant.get("text", "")
        ).strip()

        if not text:
            continue

        normalized_variants.append(
            {
                **variant,
                "type": variant_type,
                "text": text,
            }
        )

    for preferred_type in preferred_order:
        for variant in normalized_variants:
            if variant["type"] == preferred_type:
                return variant

    for fallback_type in CTA_FALLBACK_ORDER:
        for variant in normalized_variants:
            if variant["type"] == fallback_type:
                return variant

    return {
        "type": "booking",
        "text": "Book a consultation today",
    }

def _apply_selected_cta(
    profile: dict[str, Any],
    state: WebsiteState,
) -> None:
    selected_cta = select_cta_variant(
        cta_variants=profile.get(
            "cta_variants",
            [],
        ),
        conversion_strategy=profile.get(
            "conversion_strategy",
            "general",
        ),
    )

    state.cta.selected_cta_type = selected_cta["type"]
    state.cta.selected_cta = selected_cta
    state.cta.cta = selected_cta["text"]

def enforce_cta_priority_rules(
    profile: dict[str, Any],
    state: WebsiteState,
) -> None:
    website_identity = profile.get(
        "website_identity",
        {},
    )

    business_type = str(
        website_identity.get(
            "business_type",
            "",
        )
    ).lower()

    primary_cta = str(
        website_identity.get(
            "primary_cta",
            "",
        )
    ).lower()

    visible_cta = str(
        profile.get("cta", "")
    ).lower()

    ecommerce_keywords = (
        "ecommerce",
        "shop",
        "store",
        "marketplace",
        "retail",
    )

    advisory_keywords = (
        "consult",
        "consultation",
        "demo",
        "recommend",
        "expert",
        "support",
        "advisor",
    )

    if any(
        keyword in business_type
        for keyword in ecommerce_keywords
    ):

        if any(
            keyword in visible_cta
            for keyword in advisory_keywords
        ):

            website_identity["primary_cta"] = "Shop Now"
            website_identity["secondary_cta"] = "Browse Products"
            website_identity["cta_strategy"] = "purchase"

            state.cta.cta = "Shop Now"

            selected_cta = state.cta.selected_cta

            if isinstance(
                selected_cta,
                dict,
            ):
                selected_cta["text"] = "Shop Now"
                selected_cta["type"] = "purchase"

    profile["website_identity"] = website_identity

def apply_cta(
    profile: dict[str, Any],
    state: WebsiteState,
) -> None:
    _normalize_cta_variants(profile)
    _apply_selected_cta(profile, state)

    try:
        enforce_cta_priority_rules(
            profile,
            state,
        )
    except Exception:
        import traceback
        traceback.print_exc()
        raise
