from typing import Any

from backend.domain.website_state import WebsiteState


VALID_HERO_TYPES = {
    "benefit",
    "authority",
    "urgency",
    "luxury",
    "local",
    "general",
}

HERO_STRATEGY_MAP = {
    "restaurant": ["luxury", "benefit", "local", "authority", "urgency", "general"],
    "saas": ["benefit", "authority", "urgency", "general"],
    "consultant": ["authority", "benefit", "local", "general"],
    "contractor": ["local", "authority", "benefit", "urgency", "general"],
    "agency": ["authority", "benefit", "urgency", "general"],
    "medical": ["authority", "local", "benefit", "general"],
    "general": ["benefit", "authority", "general", "urgency"],
}

def _normalize_hero_variants(
    profile: dict[str, Any],
) -> None:
    variants = profile.get("hero_variants", [])

    if not isinstance(variants, list):
        variants = []

    normalized_variants = []

    for variant in variants:
        if not isinstance(variant, dict):
            continue

        hero_type = str(
            variant.get("type", "general")
        ).lower()

        if hero_type not in VALID_HERO_TYPES:
            hero_type = "general"

        title = str(
            variant.get("title", "")
        ).strip()

        subtitle = str(
            variant.get("subtitle", "")
        ).strip()

        if title and subtitle:
            normalized_variants.append(
                {
                    "type": hero_type,
                    "title": title,
                    "subtitle": subtitle,
                }
            )

    profile["hero_variants"] = normalized_variants

def _apply_selected_hero(
    profile: dict[str, Any],
    state: WebsiteState,
) -> None:
    conversion_strategy = str(
        profile.get(
            "conversion_strategy",
            "general",
        )
    ).lower()

    preferred_hero_types = HERO_STRATEGY_MAP.get(
        conversion_strategy,
        HERO_STRATEGY_MAP["general"],
    )

    variants = profile.get(
        "hero_variants",
        [],
    )

    selected_variant = None
    selected_type = "general"

    for hero_type in preferred_hero_types:
        selected_variant = next(
            (
                variant
                for variant in variants
                if variant.get("type") == hero_type
            ),
            None,
        )

        if selected_variant:
            selected_type = hero_type
            break

    if selected_variant is None and variants:
        selected_variant = variants[0]
        selected_type = selected_variant.get(
            "type",
            "general",
        )

    if selected_variant:
        state.hero.hero_title = selected_variant["title"]
        state.hero.hero_subtitle = selected_variant["subtitle"]
        state.hero.selected_hero_type = selected_type
        state.hero.selected_hero = {
            "type": selected_type,
            "headline": selected_variant["title"],
            "subheadline": selected_variant["subtitle"],
        }
    else:
        profile.setdefault(
            "selected_hero_type",
            "general",
        )

def enforce_hero_priority_rules(
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

    hero = profile.get(
        "selected_hero",
        {},
    )

    if not isinstance(
        hero,
        dict,
    ):
        return

    hero_title = str(
        hero.get(
            "headline",
            "",
        )
    )

    hero_subtitle = str(
        hero.get(
            "subheadline",
            "",
        )
    )

    # ---------------------------------------------
    # Ecommerce
    # ---------------------------------------------

    if _business_matches(
        business_type,
        "ecommerce",
        "shop",
        "store",
        "marketplace",
        "retail",
    ):

        hero["type"] = "benefit"

        state.hero.selected_hero_type = "benefit"

        profile["conversion_strategy"] = "purchase"

        state.hero.hero_title = hero_title

        state.hero.hero_subtitle = hero_subtitle

    # ---------------------------------------------
    # Consultant
    # ---------------------------------------------

    elif _business_matches(
        business_type,
        "consult",
        "coach",
        "advisor",
    ):

        hero["type"] = "authority"

        state.hero.selected_hero_type = "authority"

        profile["conversion_strategy"] = "consultation"

    # ---------------------------------------------
    # Restaurant
    # ---------------------------------------------

    elif _business_matches(
        business_type,
        "restaurant",
        "cafe",
        "food",
    ):

        hero["type"] = "luxury"

        state.hero.selected_hero_type = "luxury"

        profile["conversion_strategy"] = "booking"

        state.hero.selected_hero = hero

def apply_hero(
    profile: dict[str, Any],
    state: WebsiteState,
) -> None:
    _normalize_hero_variants(
        profile,
    )

    _apply_selected_hero(
        profile,
        state,
    )

    _enforce_hero_priority_rules(
        profile,
        state,
    )


