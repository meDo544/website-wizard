from typing import Any

from backend.domain.website_state import WebsiteState


DEFAULT_SECTION_ORDER = [
    "services",
    "features",
    "products",
    "shipping",
    "payments",
    "returns",
    "testimonials",
    "faqs",
    "contact",
    "cta",
]


INDUSTRY_SECTION_RULES = {
    "ecommerce": [
        "services",
        "features",
        "products",
        "shipping",
        "payments",
        "returns",
        "testimonials",
        "faqs",
        "contact",
        "cta",
    ],
    "restaurant": [
        "services",
        "features",
        "testimonials",
        "contact",
        "cta",
    ],
    "consultant": [
        "services",
        "testimonials",
        "features",
        "faqs",
        "contact",
        "cta",
    ],
    "contractor": [
        "services",
        "testimonials",
        "features",
        "faqs",
        "contact",
        "cta",
    ],
    "medical": [
        "services",
        "features",
        "testimonials",
        "contact",
        "cta",
    ],
    "legal": [
        "services",
        "testimonials",
        "features",
        "faqs",
        "contact",
        "cta",
    ],
    "agency": [
        "services",
        "features",
        "testimonials",
        "faqs",
        "contact",
        "cta",
    ],
    "saas": [
        "features",
        "services",
        "testimonials",
        "faqs",
        "contact",
        "cta",
    ],
    "nonprofit": [
        "features",
        "testimonials",
        "services",
        "contact",
        "cta",
    ],
    "general": DEFAULT_SECTION_ORDER,
}


def _normalize_section_order(
    profile: dict[str, Any],
) -> None:
    industry = str(
        profile.get(
            "industry",
            "general",
        )
    ).lower()

    default_order = INDUSTRY_SECTION_RULES.get(
        industry,
        DEFAULT_SECTION_ORDER,
    )

    profile["section_order"] = list(
        default_order
    )


def apply_section_order(
    profile: dict[str, Any],
    state: WebsiteState,
) -> None:
    _normalize_section_order(
        profile
    )

    section_order = profile.get(
        "section_order",
        [],
    )

    if not isinstance(
        section_order,
        list,
    ):
        section_order = []

    state.section_order.section_order = list(
        section_order
    )
