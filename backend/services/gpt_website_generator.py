# backend/services/gpt_website_generator.py

from __future__ import annotations

import json
import os
from typing import Any

import structlog
from openai import OpenAI

from backend.core.metrics import (
    record_gpt_tokens,
    track_gpt_duration,
)

logger = structlog.get_logger(__name__)

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

DEFAULT_SECTION_ORDER = [
    "services",
    "features",
    "testimonials",
    "faqs",
    "contact",
    "cta",
]

VALID_CONVERSION_STRATEGIES = {
    "restaurant",
    "saas",
    "consultant",
    "contractor",
    "agency",
    "medical",
    "general",
}

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

TRUST_STRATEGY_MAP = {
    "restaurant": ["reviews", "local", "guarantee"],
    "saas": ["security", "customers", "case_study"],
    "consultant": ["experience", "authority", "results"],
    "contractor": ["reviews", "licensed", "guarantee"],
    "agency": ["case_study", "results", "clients"],
    "medical": ["certification", "reviews", "experience"],
    "general": ["reviews"],
}

TRUST_FALLBACK_ORDER = [
    "reviews",
    "experience",
    "guarantee",
    "authority",
    "results",
    "case_study",
    "clients",
    "customers",
    "security",
    "licensed",
    "certification",
    "local",
    "general",
]

TRUST_TYPE_ALIASES = {
    "testimonial": "reviews",
    "testimonials": "reviews",
    "rating": "reviews",
    "ratings": "reviews",
    "years": "experience",
    "years_in_business": "experience",
    "proof": "results",
    "portfolio": "case_study",
    "certified": "certification",
    "licensed_insured": "licensed",
}

SOCIAL_PROOF_STRATEGY_MAP = {
    "restaurant": ["reviews", "customers", "local"],
    "saas": ["customers", "users", "case_study"],
    "consultant": ["results", "clients", "case_study"],
    "contractor": ["projects", "reviews", "local"],
    "agency": ["clients", "case_study", "results"],
    "medical": ["patients", "reviews", "certification"],
    "general": ["customers"],
}

SOCIAL_PROOF_FALLBACK_ORDER = [
    "customers",
    "clients",
    "users",
    "projects",
    "reviews",
    "results",
    "case_study",
    "community",
    "patients",
    "local",
    "certification",
    "general",
]

SOCIAL_PROOF_TYPE_ALIASES = {
    "customer": "customers",
    "client": "clients",
    "user": "users",
    "project": "projects",
    "testimonial": "reviews",
    "testimonials": "reviews",
    "rating": "reviews",
    "ratings": "reviews",
    "proof": "results",
    "portfolio": "case_study",
    "case_studies": "case_study",
    "community_members": "community",
}

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

URGENCY_STRATEGY_MAP = {
    "restaurant": ["limited_time", "seasonal", "limited_stock"],
    "saas": ["limited_time", "expiring_bonus", "limited_access"],
    "consultant": ["limited_time", "limited_spots", "expiring_bonus"],
    "contractor": ["seasonal", "limited_time", "limited_spots"],
    "agency": ["limited_spots", "limited_time", "expiring_bonus"],
    "medical": ["limited_spots", "seasonal", "limited_time"],
    "general": ["limited_time"],
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

OBJECTION_STRATEGY_MAP = {
    "restaurant": ["price", "trust", "convenience"],
    "saas": ["complexity", "price", "trust"],
    "consultant": ["trust", "price", "results"],
    "contractor": ["trust", "price", "timeline"],
    "agency": ["results", "price", "trust"],
    "medical": ["trust", "safety", "convenience"],
    "general": ["trust"],
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

VALUE_PROP_STRATEGY_MAP = {
    "restaurant": ["quality", "convenience", "cost_savings"],
    "saas": ["speed", "innovation", "cost_savings"],
    "consultant": ["expertise", "results", "reliability"],
    "contractor": ["reliability", "quality", "cost_savings"],
    "agency": ["results", "innovation", "expertise"],
    "medical": ["expertise", "reliability", "quality"],
    "general": ["quality"],
}

VALUE_PROP_FALLBACK_ORDER = [
    "quality",
    "speed",
    "cost_savings",
    "innovation",
    "expertise",
    "convenience",
    "reliability",
    "results",
    "general",
]

VALUE_PROP_TYPE_ALIASES = {
    "fast": "speed",
    "faster": "speed",
    "save_money": "cost_savings",
    "affordable": "cost_savings",
    "cutting_edge": "innovation",
    "advanced": "innovation",
    "professional": "expertise",
    "specialist": "expertise",
    "easy": "convenience",
    "trusted": "reliability",
    "dependable": "reliability",
    "outcomes": "results",
}

AUDIENCE_STRATEGY_MAP = {
    "restaurant": ["consumer", "premium", "beginner"],
    "saas": ["professional", "enterprise", "small_business"],
    "consultant": ["professional", "small_business", "premium"],
    "contractor": ["consumer", "small_business", "premium"],
    "agency": ["small_business", "enterprise", "professional"],
    "medical": ["consumer", "premium", "professional"],
    "general": ["consumer"],
}

AUDIENCE_FALLBACK_ORDER = [
    "consumer",
    "professional",
    "small_business",
    "enterprise",
    "premium",
    "beginner",
    "general",
]

AUDIENCE_TYPE_ALIASES = {
    "starter": "beginner",
    "newbie": "beginner",
    "business": "small_business",
    "smb": "small_business",
    "corporate": "enterprise",
    "company": "enterprise",
    "expert": "professional",
    "pro": "professional",
    "luxury": "premium",
    "high_end": "premium",
}

DIFFERENTIATION_STRATEGY_MAP = {
    "restaurant": ["quality", "service", "customization"],
    "saas": ["innovation", "speed", "customization"],
    "consultant": ["expertise", "service", "customization"],
    "contractor": ["quality", "service", "price"],
    "agency": ["innovation", "expertise", "customization"],
    "medical": ["expertise", "quality", "service"],
    "general": ["quality"],
}

DIFFERENTIATION_FALLBACK_ORDER = [
    "quality",
    "innovation",
    "service",
    "expertise",
    "speed",
    "price",
    "customization",
    "general",
]

DIFFERENTIATION_TYPE_ALIASES = {
    "premium": "quality",
    "advanced": "innovation",
    "technology": "innovation",
    "support": "service",
    "customer_service": "service",
    "specialist": "expertise",
    "professional": "expertise",
    "fast": "speed",
    "affordable": "price",
    "personalized": "customization",
    "tailored": "customization",
}

EMOTIONAL_TRIGGER_STRATEGY_MAP = {
    "restaurant": ["belonging", "aspiration", "confidence"],
    "saas": ["achievement", "aspiration", "confidence"],
    "consultant": ["confidence", "security", "achievement"],
    "contractor": ["security", "confidence", "belonging"],
    "agency": ["aspiration", "achievement", "status"],
    "medical": ["security", "confidence", "belonging"],
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

BUYER_MOTIVATION_STRATEGY_MAP = {
    "restaurant": ["comfort", "save_money", "status"],
    "saas": ["save_time", "growth", "success"],
    "consultant": ["growth", "success", "security"],
    "contractor": ["security", "save_money", "comfort"],
    "agency": ["growth", "status", "success"],
    "medical": ["security", "comfort", "save_time"],
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

PAIN_POINT_STRATEGY_MAP = {
    "restaurant": ["time", "frustration", "cost"],
    "saas": ["time", "complexity", "competition"],
    "consultant": ["uncertainty", "risk", "competition"],
    "contractor": ["risk", "cost", "time"],
    "agency": ["competition", "complexity", "time"],
    "medical": ["risk", "uncertainty", "time"],
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

def _get_openai_model() -> str:
    return os.getenv(
        "OPENAI_MODEL",
        "gpt-4.1-mini",
    )

def _extract_usage(response: Any) -> dict[str, int]:

    usage = getattr(response, "usage", None)

    if usage is None:
        return {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
        }

    return {
        "prompt_tokens": int(
            getattr(usage, "prompt_tokens", 0) or 0
        ),
        "completion_tokens": int(
            getattr(usage, "completion_tokens", 0) or 0
        ),
        "total_tokens": int(
            getattr(usage, "total_tokens", 0) or 0
        ),
    }

def _normalize_section_order(
    profile: dict[str, Any],
) -> None:
    section_order = profile.get(
        "section_order",
        DEFAULT_SECTION_ORDER,
    )

    if not isinstance(section_order, list):
        profile["section_order"] = DEFAULT_SECTION_ORDER
        return

    normalized_order = [
        section
        for section in section_order
        if section in DEFAULT_SECTION_ORDER
    ]

    profile["section_order"] = (
        normalized_order
        or DEFAULT_SECTION_ORDER
    )

def _normalize_conversion_strategy(
    profile: dict[str, Any],
) -> None:

    strategy = str(
        profile.get(
            "conversion_strategy",
            "general",
        )
    ).lower()

    if strategy not in VALID_CONVERSION_STRATEGIES:
        strategy = "general"

    profile["conversion_strategy"] = strategy

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

def _normalize_offer_variants(
    profile: dict[str, Any],
) -> None:
    variants = profile.get("offer_variants", [])

    if not isinstance(variants, list):
        variants = []

    normalized_variants = []

    for variant in variants:
        if not isinstance(variant, dict):
            continue

        offer_type = normalize_offer_type(
            variant.get("type")
        )

        headline = str(
            variant.get("headline", "")
        ).strip()

        if headline:
            normalized_variants.append(
                {
                    "type": offer_type,
                    "headline": headline,
                }
            )

def _normalize_trust_variants(
    profile: dict[str, Any],
) -> None:

    variants = profile.get(
        "trust_variants",
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

        trust_type = normalize_trust_type(
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
                    "type": trust_type,
                    "headline": headline,
                }
            )

    profile["trust_variants"] = normalized_variants

def _normalize_social_proof_variants(
    profile: dict[str, Any],
) -> None:

    variants = profile.get(
        "social_proof_variants",
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

        social_proof_type = (
            normalize_social_proof_type(
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
                    "type": social_proof_type,
                    "headline": headline,
                }
            )

    profile[
        "social_proof_variants"
    ] = normalized_variants

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

def _normalize_value_prop_variants(
    profile: dict[str, Any],
) -> None:

    variants = profile.get(
        "value_prop_variants",
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

        value_prop_type = (
            normalize_value_prop_type(
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
                    "type": value_prop_type,
                    "headline": headline,
                }
            )

    profile[
        "value_prop_variants"
    ] = normalized_variants

def _normalize_audience_variants(
    profile: dict[str, Any],
) -> None:

    variants = profile.get(
        "audience_variants",
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

        audience_type = (
            normalize_audience_type(
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
                    "type": audience_type,
                    "headline": headline,
                }
            )

    profile[
        "audience_variants"
    ] = normalized_variants

def _normalize_differentiation_variants(
    profile: dict[str, Any],
) -> None:

    variants = profile.get(
        "differentiation_variants",
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

        differentiation_type = (
            normalize_differentiation_type(
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
                    "type": differentiation_type,
                    "headline": headline,
                }
            )

    profile[
        "differentiation_variants"
    ] = normalized_variants

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

def normalize_cta_type(cta_type: str | None) -> str:
    if not cta_type:
        return "general"

    normalized = str(cta_type).strip().lower().replace("-", "_").replace(" ", "_")
    return CTA_TYPE_ALIASES.get(normalized, normalized)

def normalize_offer_type(
    offer_type: str | None,
) -> str:

    if not offer_type:
        return "general"

    normalized = (
        str(offer_type)
        .strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )

    return OFFER_TYPE_ALIASES.get(
        normalized,
        normalized,
    )

def normalize_trust_type(
    trust_type: str | None,
) -> str:

    if not trust_type:
        return "general"

    normalized = (
        str(trust_type)
        .strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )

    return TRUST_TYPE_ALIASES.get(
        normalized,
        normalized,
    )

def normalize_social_proof_type(
    social_proof_type: str | None,
) -> str:

    if not social_proof_type:
        return "general"

    normalized = (
        str(social_proof_type)
        .strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )

    return SOCIAL_PROOF_TYPE_ALIASES.get(
        normalized,
        normalized,
    )

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

def normalize_value_prop_type(
    value_prop_type: str | None,
) -> str:

    if not value_prop_type:
        return "general"

    normalized = (
        str(value_prop_type)
        .strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )

    return VALUE_PROP_TYPE_ALIASES.get(
        normalized,
        normalized,
    )

def normalize_audience_type(
    audience_type: str | None,
) -> str:

    if not audience_type:
        return "general"

    normalized = (
        str(audience_type)
        .strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )

    return AUDIENCE_TYPE_ALIASES.get(
        normalized,
        normalized,
    )

def normalize_differentiation_type(
    differentiation_type: str | None,
) -> str:

    if not differentiation_type:
        return "general"

    normalized = (
        str(differentiation_type)
        .strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )

    return DIFFERENTIATION_TYPE_ALIASES.get(
        normalized,
        normalized,
    )

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

def select_cta_variant(
    cta_variants: list[dict],
    conversion_strategy: str | None = None,
) -> dict:
    strategy = normalize_cta_type(conversion_strategy)
    preferred_order = CTA_STRATEGY_MAP.get(strategy, CTA_STRATEGY_MAP["general"])

    normalized_variants = []
    for variant in cta_variants or []:
        if not isinstance(variant, dict):
            continue

        variant_type = normalize_cta_type(variant.get("type"))
        text = (variant.get("text") or "").strip()

        if not text:
            continue

        normalized_variants.append({
            **variant,
            "type": variant_type,
            "text": text,
        })

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

def select_offer_variant(
    offer_variants: list[dict],
    conversion_strategy: str | None = None,
) -> dict:

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

def select_trust_variant(
    trust_variants: list[dict],
    conversion_strategy: str | None = None,
) -> dict:

    strategy = normalize_trust_type(
        conversion_strategy
    )

    preferred_order = TRUST_STRATEGY_MAP.get(
        strategy,
        TRUST_STRATEGY_MAP["general"],
    )

    normalized_variants = []

    for variant in trust_variants or []:

        if not isinstance(
            variant,
            dict,
        ):
            continue

        trust_type = normalize_trust_type(
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
                "type": trust_type,
                "headline": headline,
            }
        )

    for preferred_type in preferred_order:

        for variant in normalized_variants:

            if variant["type"] == preferred_type:
                return variant

    for fallback_type in TRUST_FALLBACK_ORDER:

        for variant in normalized_variants:

            if variant["type"] == fallback_type:
                return variant

    return {
        "type": "discount",
        "headline": "Special Trust Available Today",
    }

def select_social_proof_variant(
    social_proof_variants: list[dict],
    conversion_strategy: str | None = None,
) -> dict:

    strategy = normalize_social_proof_type(
        conversion_strategy
    )

    preferred_order = (
        SOCIAL_PROOF_STRATEGY_MAP.get(
            strategy,
            SOCIAL_PROOF_STRATEGY_MAP[
                "general"
            ],
        )
    )

    normalized_variants = []

    for variant in (
        social_proof_variants or []
    ):

        if not isinstance(
            variant,
            dict,
        ):
            continue

        social_proof_type = (
            normalize_social_proof_type(
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
                "type": social_proof_type,
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
        SOCIAL_PROOF_FALLBACK_ORDER
    ):

        for variant in normalized_variants:

            if (
                variant["type"]
                == fallback_type
            ):
                return variant

    return {
        "type": "customers",
        "headline": (
            "Trusted by Customers"
        ),
    }

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

def select_value_prop_variant(
    value_prop_variants: list[dict],
    conversion_strategy: str | None = None,
) -> dict:

    strategy = normalize_value_prop_type(
        conversion_strategy
    )

    preferred_order = (
        VALUE_PROP_STRATEGY_MAP.get(
            strategy,
            VALUE_PROP_STRATEGY_MAP[
                "general"
            ],
        )
    )

    normalized_variants = []

    for variant in (
        value_prop_variants or []
    ):

        if not isinstance(
            variant,
            dict,
        ):
            continue

        value_prop_type = (
            normalize_value_prop_type(
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
                "type": value_prop_type,
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
        VALUE_PROP_FALLBACK_ORDER
    ):

        for variant in normalized_variants:

            if (
                variant["type"]
                == fallback_type
            ):
                return variant

    return {
        "type": "quality",
        "headline": (
            "Premium Quality You Can Trust"
        ),
    }

def select_audience_variant(
    audience_variants: list[dict],
    conversion_strategy: str | None = None,
) -> dict:

    strategy = normalize_audience_type(
        conversion_strategy
    )

    preferred_order = (
        AUDIENCE_STRATEGY_MAP.get(
            strategy,
            AUDIENCE_STRATEGY_MAP[
                "general"
            ],
        )
    )

    normalized_variants = []

    for variant in (
        audience_variants or []
    ):

        if not isinstance(
            variant,
            dict,
        ):
            continue

        audience_type = (
            normalize_audience_type(
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
                "type": audience_type,
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
        AUDIENCE_FALLBACK_ORDER
    ):

        for variant in normalized_variants:

            if (
                variant["type"]
                == fallback_type
            ):
                return variant

    return {
        "type": "consumer",
        "headline": (
            "Designed for Everyday Customers"
        ),
    }

def select_differentiation_variant(
    differentiation_variants: list[dict],
    conversion_strategy: str | None = None,
) -> dict:

    strategy = normalize_differentiation_type(
        conversion_strategy
    )

    preferred_order = (
        DIFFERENTIATION_STRATEGY_MAP.get(
            strategy,
            DIFFERENTIATION_STRATEGY_MAP[
                "general"
            ],
        )
    )

    normalized_variants = []

    for variant in (
        differentiation_variants or []
    ):

        if not isinstance(
            variant,
            dict,
        ):
            continue

        differentiation_type = (
            normalize_differentiation_type(
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
                "type": differentiation_type,
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
        DIFFERENTIATION_FALLBACK_ORDER
    ):

        for variant in normalized_variants:

            if (
                variant["type"]
                == fallback_type
            ):
                return variant

    return {
        "type": "quality",
        "headline": (
            "Higher Quality Than Typical Alternatives"
        ),
    }

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

def _apply_selected_hero(
    profile: dict[str, Any],
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
        profile["hero_title"] = selected_variant["title"]
        profile["hero_subtitle"] = selected_variant["subtitle"]
        profile["selected_hero_type"] = selected_type
    else:
        profile.setdefault(
            "selected_hero_type",
            "general",
        )

def _apply_selected_cta(
    profile: dict[str, Any],
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

    profile["selected_cta_type"] = selected_cta["type"]
    profile["selected_cta"] = selected_cta
    profile["cta"] = selected_cta["text"]

def _apply_selected_offer(
    profile: dict[str, Any],
) -> None:

    selected_offer = select_offer_variant(
        offer_variants=profile.get(
            "offer_variants",
            [],
        ),
        conversion_strategy=profile.get(
            "conversion_strategy",
            "general",
        ),
    )

    profile["selected_offer_type"] = (
        selected_offer["type"]
    )

    profile["selected_offer"] = (
        selected_offer
    )

def _apply_selected_trust(
    profile: dict[str, Any],
) -> None:

    selected_trust = select_trust_variant(
        trust_variants=profile.get(
            "trust_variants",
            [],
        ),
        conversion_strategy=profile.get(
            "conversion_strategy",
            "general",
        ),
    )

    profile["selected_trust_type"] = (
        selected_trust["type"]
    )

    profile["selected_trust"] = (
        selected_trust
    )

def _apply_selected_social_proof(
    profile: dict[str, Any],
) -> None:

    selected_social_proof = (
        select_social_proof_variant(
            social_proof_variants=profile.get(
                "social_proof_variants",
                [],
            ),
            conversion_strategy=profile.get(
                "conversion_strategy",
                "general",
            ),
        )
    )

    profile[
        "selected_social_proof_type"
    ] = selected_social_proof["type"]

    profile[
        "selected_social_proof"
    ] = selected_social_proof

def _apply_selected_risk_reversal(
    profile: dict[str, Any],
) -> None:

    selected_risk_reversal = (
        select_risk_reversal_variant(
            risk_reversal_variants=profile.get(
                "risk_reversal_variants",
                [],
            ),
            conversion_strategy=profile.get(
                "conversion_strategy",
                "general",
            ),
        )
    )

    profile[
        "selected_risk_reversal_type"
    ] = selected_risk_reversal["type"]

    profile[
        "selected_risk_reversal"
    ] = selected_risk_reversal

def _apply_selected_urgency(
    profile: dict[str, Any],
) -> None:

    selected_urgency = (
        select_urgency_variant(
            urgency_variants=profile.get(
                "urgency_variants",
                [],
            ),
            conversion_strategy=profile.get(
                "conversion_strategy",
                "general",
            ),
        )
    )

    profile[
        "selected_urgency_type"
    ] = selected_urgency["type"]

    profile[
        "selected_urgency"
    ] = selected_urgency

def _apply_selected_objection(
    profile: dict[str, Any],
) -> None:

    selected_objection = (
        select_objection_variant(
            objection_variants=profile.get(
                "objection_variants",
                [],
            ),
            conversion_strategy=profile.get(
                "conversion_strategy",
                "general",
            ),
        )
    )

    profile[
        "selected_objection_type"
    ] = selected_objection["type"]

    profile[
        "selected_objection"
    ] = selected_objection

def _apply_selected_value_prop(
    profile: dict[str, Any],
) -> None:

    selected_value_prop = (
        select_value_prop_variant(
            value_prop_variants=profile.get(
                "value_prop_variants",
                [],
            ),
            conversion_strategy=profile.get(
                "conversion_strategy",
                "general",
            ),
        )
    )

    profile[
        "selected_value_prop_type"
    ] = selected_value_prop["type"]

    profile[
        "selected_value_prop"
    ] = selected_value_prop

def _apply_selected_audience(
    profile: dict[str, Any],
) -> None:

    selected_audience = (
        select_audience_variant(
            audience_variants=profile.get(
                "audience_variants",
                [],
            ),
            conversion_strategy=profile.get(
                "conversion_strategy",
                "general",
            ),
        )
    )

    profile[
        "selected_audience_type"
    ] = selected_audience["type"]

    profile[
        "selected_audience"
    ] = selected_audience

def _apply_selected_differentiation(
    profile: dict[str, Any],
) -> None:

    selected_differentiation = (
        select_differentiation_variant(
            differentiation_variants=profile.get(
                "differentiation_variants",
                [],
            ),
            conversion_strategy=profile.get(
                "conversion_strategy",
                "general",
            ),
        )
    )

    profile[
        "selected_differentiation_type"
    ] = selected_differentiation["type"]

    profile[
        "selected_differentiation"
    ] = selected_differentiation

def _apply_selected_emotional_trigger(
    profile: dict[str, Any],
) -> None:

    selected_emotional_trigger = (
        select_emotional_trigger_variant(
            emotional_trigger_variants=profile.get(
                "emotional_trigger_variants",
                [],
            ),
            conversion_strategy=profile.get(
                "conversion_strategy",
                "general",
            ),
        )
    )

    profile[
        "selected_emotional_trigger_type"
    ] = selected_emotional_trigger["type"]

    profile[
        "selected_emotional_trigger"
    ] = selected_emotional_trigger

def _apply_selected_buyer_motivation(
    profile: dict[str, Any],
) -> None:

    selected_buyer_motivation = (
        select_buyer_motivation_variant(
            buyer_motivation_variants=profile.get(
                "buyer_motivation_variants",
                [],
            ),
            conversion_strategy=profile.get(
                "conversion_strategy",
                "general",
            ),
        )
    )

    profile[
        "selected_buyer_motivation_type"
    ] = selected_buyer_motivation["type"]

    profile[
        "selected_buyer_motivation"
    ] = selected_buyer_motivation

def _apply_selected_pain_point(
    profile: dict[str, Any],
) -> None:

    selected_pain_point = (
        select_pain_point_variant(
            pain_point_variants=profile.get(
                "pain_point_variants",
                [],
            ),
            conversion_strategy=profile.get(
                "conversion_strategy",
                "general",
            ),
        )
    )

    profile[
        "selected_pain_point_type"
    ] = selected_pain_point["type"]

    profile[
        "selected_pain_point"
    ] = selected_pain_point

def generate_business_profile(
    *,
    prompt: str,
    business_type: str,
    user_id: str = "system",
) -> dict[str, Any]:
    """
    Generate structured website content
    from a business description.
    """

    model = _get_openai_model()

    logger.info(
        "Website generation started",
        business_type=business_type,
        model=model,
    )

    with track_gpt_duration(
        model=model,
        user_id=user_id,
    ) as metrics:

        try:

            system_prompt = """
You are Website Wizard.

Generate rich website content, branding, and landing page structure for a small business.

Return ONLY valid JSON.

Return realistic, business-specific content.

Generate at least:
- 3 services
- 3 features
- 3 testimonials
- 3 FAQs

Also generate a brand identity:
- primary color as a hex code
- secondary color as a hex code
- font family suggestion
- logo text

Also generate a conversion-focused landing page section order.

Available section_order values:
- services
- features
- testimonials
- faqs
- contact
- cta

section_order must be an array.

Also generate:

"conversion_strategy"

Valid values:

- restaurant
- saas
- consultant
- contractor
- agency
- medical
- general

Choose the highest-converting layout based on business type.

Examples:

Restaurant:
services → testimonials → features → contact → cta

SaaS:
features → services → testimonials → faqs → cta → contact

Consultant:
features → testimonials → services → cta → contact

Contractor:
services → testimonials → faqs → contact → cta

Agency:
features → services → testimonials → faqs → cta → contact

Medical:
services → features → testimonials → faqs → contact → cta

Do not blindly copy examples.
Choose the best conversion strategy for the business.

Also generate hero_variants.

Generate at least 3 hero variants.

Valid hero types:

- benefit
- authority
- urgency
- luxury
- local
- general

Each hero variant must contain:

{
  "type": "",
  "title": "",
  "subtitle": ""
}

Also generate:

cta_variants

Generate at least 3 CTA variants.

Valid CTA types:

- booking
- quote
- purchase
- consultation
- demo
- trial
- appointment
- general

Each CTA variant must contain:

{
  "type": "",
  "text": ""
}

Also generate:

social_proof_variants

social_proof_variants is REQUIRED.

Generate at least 3 social proof variants.

Valid social proof types:

- customers
- clients
- users
- projects
- reviews
- results
- case_study
- community
- patients
- local
- certification
- general

Each social proof variant must contain:

{
  "type": "",
  "headline": ""
}

Also generate:

risk_reversal_variants

risk_reversal_variants is REQUIRED.

Generate at least 3 risk reversal variants.

Valid risk reversal types:

- guarantee
- money_back
- free_trial
- warranty
- consultation
- bonus
- general

Each risk reversal variant must contain:

{
  "type": "",
  "headline": ""
}

Also generate:

urgency_variants

urgency_variants is REQUIRED.

Generate at least 3 urgency variants.

Valid urgency types:

- limited_time
- limited_spots
- limited_stock
- seasonal
- expiring_bonus
- limited_access
- general

Each urgency variant must contain:

{
  "type": "",
  "headline": ""
}

Also generate:

objection_variants

objection_variants is REQUIRED.

Generate at least 3 objection variants.

Valid objection types:

- price
- trust
- complexity
- results
- timeline
- safety
- convenience
- general

Each objection variant must contain:

{
  "type": "",
  "headline": ""
}

Also generate:

value_prop_variants

value_prop_variants is REQUIRED.

Generate at least 3 value proposition variants.

Valid value proposition types:

- speed
- quality
- cost_savings
- innovation
- expertise
- convenience
- reliability
- results
- general

Each value proposition variant must contain:

{
  "type": "",
  "headline": ""
}

Also generate:

audience_variants

audience_variants is REQUIRED.

Generate at least 3 audience variants.

Valid audience types:

- beginner
- professional
- enterprise
- small_business
- consumer
- premium
- general

Each audience variant must contain:

{
  "type": "",
  "headline": ""
}

Also generate:

differentiation_variants

differentiation_variants is REQUIRED.

Generate at least 3 differentiation variants.

Valid differentiation types:

- quality
- innovation
- service
- speed
- price
- expertise
- customization
- general

Each differentiation variant must contain:

{
  "type": "",
  "headline": ""
}

Also generate:

emotional_trigger_variants

emotional_trigger_variants is REQUIRED.

Generate at least 3 emotional trigger variants.

Valid emotional trigger types:

- aspiration
- security
- status
- belonging
- achievement
- fear_of_missing_out
- confidence
- general

Each emotional trigger variant must contain:

{
  "type": "",
  "headline": ""
}

Also generate:

buyer_motivation_variants

buyer_motivation_variants is REQUIRED.

Generate at least 3 buyer motivation variants.

Valid buyer motivation types:

- save_time
- save_money
- growth
- success
- comfort
- security
- status
- general

Each buyer motivation variant must contain:

{
  "type": "",
  "headline": ""
}

Also generate:

pain_point_variants

pain_point_variants is REQUIRED.

Generate at least 3 pain point variants.

Valid pain point types:

- cost
- time
- complexity
- risk
- frustration
- competition
- uncertainty
- general

Each pain point variant must contain:

{
  "type": "",
  "headline": ""
}

Also generate:

selected_hero_type

Choose the hero most likely to convert for the business.

Use this exact JSON structure:

{
  "branding": {
    "primary_color": "",
    "secondary_color": "",
    "font_family": "",
    "logo_text": ""
  },

  "business_name": "",
  "tagline": "",

  "hero_variants": [
    {
      "type": "benefit",
      "title": "",
      "subtitle": ""
    },
    {
      "type": "authority",
      "title": "",
      "subtitle": ""
    },
    {
      "type": "urgency",
      "title": "",
      "subtitle": ""
    }
  ],

  "selected_hero_type": "benefit",

  "hero_title": "",
  "hero_subtitle": "",

  "about": "",

  "services": [
    "",
    "",
    ""
  ],

  "features": [
    "",
    "",
    ""
  ],

  "testimonials": [
    {
      "name": "",
      "quote": ""
    },
    {
      "name": "",
      "quote": ""
    },
    {
      "name": "",
      "quote": ""
    }
  ],

  "faqs": [
    {
      "question": "",
      "answer": ""
    },
    {
      "question": "",
      "answer": ""
    },
    {
      "question": "",
      "answer": ""
    }
  ],

  "contact": {
    "phone": "",
    "email": "",
    "address": ""
  },

  "cta": "",

  "cta_variants": [
    {
      "type": "booking",
      "text": "Book your appointment today"
    },
    {
      "type": "quote",
      "text": "Request a free quote"
    },
    {
      "type": "purchase",
      "text": "Get started today"
    }
  ],

  "offer_variants": [
    {
      "type": "discount",
      "headline": "Save 20% Today"
    },
    {
      "type": "consultation",
      "headline": "Free Strategy Session"
    },
    {
      "type": "bonus",
      "headline": "Free Setup Included"
    }
  ],

  "social_proof_variants": [
    {
      "type": "customers",
      "headline": "Trusted by 5,000+ Customers"
    },
    {
      "type": "projects",
      "headline": "Over 1,200 Successful Projects"
    },
    {
      "type": "community",
      "headline": "Join Our Growing Community"
    }
  ],

  "risk_reversal_variants": [
    {
      "type": "guarantee",
      "headline": "100% Satisfaction Guarantee"
    },
    {
      "type": "money_back",
      "headline": "30-Day Money Back Guarantee"
    },
    {
      "type": "free_trial",
      "headline": "Try It Risk Free"
    }
  ],

  "urgency_variants": [
    {
      "type": "limited_time",
      "headline": "Offer Ends This Week"
    },
    {
      "type": "limited_spots",
      "headline": "Only 5 Spots Remaining"
    },
    {
      "type": "seasonal",
      "headline": "Summer Promotion Ends Soon"
    }
  ],

  "objection_variants": [
    {
      "type": "price",
      "headline": "Affordable Options Available"
    },
    {
      "type": "complexity",
      "headline": "Easy Setup and Ongoing Support"
    },
    {
      "type": "trust",
      "headline": "Trusted by Thousands of Customers"
    }
  ],

  "value_prop_variants": [
    {
      "type": "quality",
      "headline": "Premium Quality You Can Trust"
    },
    {
      "type": "speed",
      "headline": "Get Results Faster"
    },
    {
      "type": "cost_savings",
      "headline": "Save Time and Money"
    }
  ],

  "audience_variants": [
    {
      "type": "consumer",
      "headline": "Perfect for Everyday Customers"
    },
    {
      "type": "professional",
      "headline": "Built for Professionals"
    },
    {
      "type": "small_business",
      "headline": "Designed for Growing Businesses"
    }
  ],

  "differentiation_variants": [
    {
      "type": "quality",
      "headline": "Higher Quality Than Typical Alternatives"
    },
    {
      "type": "innovation",
      "headline": "Advanced Technology That Sets Us Apart"
    },
    {
      "type": "service",
      "headline": "Personalized Support Every Step of the Way"
    }
  ],

  "emotional_trigger_variants": [
    {
      "type": "aspiration",
      "headline": "Achieve More With Less Effort"
    },
    {
      "type": "security",
      "headline": "Feel Confident in Every Purchase"
    },
    {
      "type": "status",
      "headline": "Stand Out With Premium Solutions"
    }
  ],

  "buyer_motivation_variants": [
    {
      "type": "save_time",
      "headline": "Get More Done in Less Time"
    },
    {
      "type": "save_money",
      "headline": "Keep More Money in Your Pocket"
    },
    {
      "type": "growth",
      "headline": "Accelerate Your Personal and Business Growth"
    }
  ],

  "pain_point_variants": [
    {
      "type": "time",
      "headline": "Stop Wasting Time on Outdated Solutions"
    },
    {
      "type": "cost",
      "headline": "Reduce Unnecessary Expenses"
    },
    {
      "type": "risk",
      "headline": "Avoid Costly Mistakes"
    }
  ],

  "conversion_strategy": "general",

  "section_order": [
    "services",
    "features",
    "testimonials",
    "faqs",
    "contact",
    "cta"
  ],

  "seo_title": "",
  "seo_description": ""
}
"""

            response = client.chat.completions.create(
                model=model,
                temperature=0.7,
                response_format={
                    "type": "json_object"
                },
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Business Type: {business_type}\n\n"
                            f"Business Description:\n{prompt}"
                        ),
                    },
                ],
            )

            usage = _extract_usage(response)

            record_gpt_tokens(
                model=model,
                user_id=user_id,
                prompt_tokens=usage["prompt_tokens"],
                completion_tokens=usage["completion_tokens"],
                total_tokens=usage["total_tokens"],
            )

            content = (
                response.choices[0].message.content
                or "{}"
            )

            profile = json.loads(content)

            if not profile.get("offer_variants"):
                profile["offer_variants"] = [
                    {
                        "type": "discount",
                        "headline": "Special Offer Available Today",
                    },
                    {
                        "type": "consultation",
                        "headline": "Free Consultation Available",
                    },
                    {
                        "type": "bonus",
                        "headline": "Bonus Service Included",
                    },
                ]

            branding = profile.get(
                "branding",
                {},
            )

            if not profile.get("trust_variants"):
                profile["trust_variants"] = [
                    {
                        "type": "reviews",
                        "headline": "Trusted by Happy Customers",
                    },
                    {
                        "type": "experience",
                        "headline": "Experienced Professionals You Can Rely On",
                    },
                    {
                        "type": "guarantee",
                        "headline": "Satisfaction Guaranteed",
                    },
                ]

            if not profile.get("social_proof_variants"):
                profile["social_proof_variants"] = [
                    {
                        "type": "customers",
                        "headline": "Trusted by Customers",
                    },
                    {
                        "type": "projects",
                        "headline": "Successful Projects Delivered",
                    },
                    {
                        "type": "community",
                        "headline": "Join Our Growing Community",
                    },
                ]

            if not profile.get("risk_reversal_variants"):
                profile["risk_reversal_variants"] = [
                    {
                        "type": "guarantee",
                        "headline": "100% Satisfaction Guarantee",
                    },
                    {
                        "type": "money_back",
                        "headline": "30-Day Money Back Guarantee",
                    },
                    {
                        "type": "free_trial",
                        "headline": "Try It Risk Free",
                    },
                ]

            if not profile.get("urgency_variants"):
                profile["urgency_variants"] = [
                    {
                        "type": "limited_time",
                        "headline": "Offer Ends This Week",
                    },
                    {
                        "type": "limited_spots",
                        "headline": "Only 5 Spots Remaining",
                    },
                    {
                        "type": "seasonal",
                        "headline": "Seasonal Promotion Available",
                    },
                ]

            if not profile.get("objection_variants"):
                profile["objection_variants"] = [
                    {
                        "type": "price",
                        "headline": "Affordable Options Available",
                    },
                    {
                        "type": "complexity",
                        "headline": "Easy Setup and Ongoing Support",
                    },
                    {
                        "type": "trust",
                        "headline": "Trusted by Thousands of Customers",
                    },
                ]

            if not profile.get("value_prop_variants"):
                profile["value_prop_variants"] = [
                    {
                        "type": "quality",
                        "headline": "Premium Quality You Can Trust",
                    },
                    {
                        "type": "speed",
                        "headline": "Get Results Faster",
                    },
                    {
                        "type": "cost_savings",
                        "headline": "Save Time and Money",
                    },
                ]

            if not profile.get("audience_variants"):
                profile["audience_variants"] = [
                    {
                        "type": "consumer",
                        "headline": "Perfect for Everyday Customers",
                    },
                    {
                        "type": "professional",
                        "headline": "Built for Professionals",
                    },
                    {
                        "type": "small_business",
                        "headline": "Designed for Growing Businesses",
                    },
                 ]

            if not profile.get("differentiation_variants"):
                profile["differentiation_variants"] = [
                    {
                        "type": "quality",
                        "headline": (
                            "Higher Quality Than Typical Alternatives"
                        ),
                    },
                    {
                        "type": "innovation",
                        "headline": (
                            "Advanced Technology That Sets Us Apart"
                        ),
                    },
                    {
                        "type": "service",
                        "headline": (
                            "Personalized Support Every Step of the Way"
                        ),
                    },
                 ]

            if not profile.get("emotional_trigger_variants"):
                profile["emotional_trigger_variants"] = [
                    {
                        "type": "aspiration",
                        "headline": (
                            "Achieve More With Less Effort"
                        ),
                    },
                    {
                        "type": "security",
                        "headline": (
                            "Feel Confident in Every Purchase"
                        ),
                    },
                    {
                        "type": "status",
                        "headline": (
                            "Stand Out With Premium Solutions"
                        ),
                    },
                ]

            if not profile.get("buyer_motivation_variants"):
                profile["buyer_motivation_variants"] = [
                    {
                        "type": "save_time",
                        "headline": (
                            "Get More Done in Less Time"
                        ),
                    },
                    {
                        "type": "save_money",
                        "headline": (
                            "Keep More Money in Your Pocket"
                        ),
                    },
                    {
                        "type": "growth",
                        "headline": (
                            "Accelerate Your Personal and Business Growth"
                        ),
                    },
                ]

            if not profile.get("pain_point_variants"):
                profile["pain_point_variants"] = [
                    {
                        "type": "time",
                        "headline": (
                            "Stop Wasting Time on Outdated Solutions"
                        ),
                    },
                    {
                        "type": "cost",
                        "headline": (
                            "Reduce Unnecessary Expenses"
                        ),
                    },
                    {
                        "type": "risk",
                        "headline": (
                            "Avoid Costly Mistakes"
                        ),
                    },
                ]

            if "logo_text\n" in branding:
                branding["logo_text"] = branding.pop(
                    "logo_text\n"
                )

            profile["branding"] = branding

            _normalize_section_order(
                profile
            )

            _normalize_conversion_strategy(
                profile
            )

            _normalize_hero_variants(
                profile
            )

            _normalize_cta_variants(
                profile
            )

            _normalize_offer_variants(
                profile
            )

            _normalize_trust_variants(
                profile
            )

            _normalize_social_proof_variants(
                profile
            )

            _normalize_risk_reversal_variants(
                profile
            )

            _normalize_urgency_variants(
                profile
            )

            _normalize_objection_variants(
                profile
            )

            _normalize_value_prop_variants(
                profile
            )

            _normalize_audience_variants(
                profile
            )

            _normalize_differentiation_variants(
                profile
            )

            _normalize_emotional_trigger_variants(
                profile
            )

            _normalize_buyer_motivation_variants(
                profile
            )

            _normalize_pain_point_variants(
                profile
            )

            _apply_selected_hero(
                profile
            )

            _apply_selected_cta(
                profile
            )

            _apply_selected_offer(
                profile
            )

            _apply_selected_trust(
                profile
            )

            _apply_selected_social_proof(
                profile
            )

            _apply_selected_risk_reversal(
                profile
            )

            _apply_selected_urgency(
                profile
            )

            _apply_selected_objection(
                profile
            )

            _apply_selected_value_prop(
                profile
            )

            _apply_selected_audience(
                profile
            )

            _apply_selected_differentiation(
                profile
            )

            _apply_selected_emotional_trigger(
                profile
            )

            _apply_selected_buyer_motivation(
                profile
            )

            _apply_selected_pain_point(
                profile
            )

            metrics["status"] = "success"

            logger.info(
                "Website generation completed",
                business_type=business_type,
                model=model,
                total_tokens=usage["total_tokens"],
                conversion_strategy=profile.get(
                    "conversion_strategy",
                ),
                section_order=profile.get(
                    "section_order",
                ),
                selected_hero_type=profile.get(
                    "selected_hero_type",
                ),
                selected_cta_type=profile.get(
                    "selected_cta_type",
                ),
                selected_offer_type=profile.get(
                    "selected_offer_type",
                ),
                selected_trust_type=profile.get(
                    "selected_trust_type",
                ),
                selected_social_proof_type=profile.get(
                    "selected_social_proof_type",
                ),
                selected_risk_reversal_type=profile.get(
                    "selected_risk_reversal_type",
                ),
                selected_urgency_type=profile.get(
                    "selected_urgency_type",
                ),
                selected_objection_type=profile.get(
                    "selected_objection_type",
                ),
                selected_differentiation_type=profile.get(
                    "selected_differentiation_type",
                ),
                selected_value_prop_type=profile.get(
                    "selected_value_prop_type",
                ),
                selected_audience_type=profile.get(
                    "selected_audience_type",
                ),
                selected_emotional_trigger_type=profile.get(
                    "selected_emotional_trigger_type",
                ),
                selected_buyer_motivation_type=profile.get(
                    "selected_buyer_motivation_type",
                ),
                selected_pain_point_type=profile.get(
                    "selected_pain_point_type",
                ),
                cta=profile.get(
                    "cta",
                ),
            )

            profile["_usage"] = usage
            profile["_model"] = model

            return profile

        except Exception as exc:

            metrics["status"] = "failure"

            logger.exception(
                "Website generation failed",
                business_type=business_type,
                model=model,
                failure_type=exc.__class__.__name__,
            )

            raise
