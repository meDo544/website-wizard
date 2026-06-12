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

    profile["offer_variants"] = normalized_variants

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

            _apply_selected_hero(
                profile
            )

            _apply_selected_cta(
                profile
            )

            _apply_selected_offer(
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
