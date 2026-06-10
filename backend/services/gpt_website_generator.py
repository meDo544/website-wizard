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

