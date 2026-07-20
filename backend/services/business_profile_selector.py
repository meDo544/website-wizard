from typing import Any

VALID_TEMPLATE_NAMES = {
    "modern",
    "classic",
    "minimal",
    "luxury",
}

INDUSTRY_TEMPLATE_MAP = {
    "ecommerce": "modern",
    "restaurant": "luxury",
    "medical": "classic",
    "legal": "classic",
    "contractor": "classic",
    "consultant": "classic",
    "agency": "modern",
    "saas": "modern",
    "nonprofit": "minimal",
    "general": "modern",
}

VALID_LAYOUT_TYPES = {
    "authority",
    "catalog",
    "product",
    "visual",
    "trust",
    "mission",
    "general",
}

INDUSTRY_LAYOUT_MAP = {
    "consultant": "authority",
    "legal": "authority",
    "medical": "trust",
    "contractor": "authority",
    "restaurant": "visual",
    "hotel": "visual",
    "ecommerce": "catalog",
    "saas": "product",
    "agency": "product",
    "nonprofit": "mission",
    "general": "general",
}

def _business_matches(
    business_type: str,
    *keywords: str,
) -> bool:

    business_type = business_type.lower()

    return any(
        keyword.lower() in business_type
        for keyword in keywords
    )

INDUSTRY_TYPES = {
    "ecommerce",
    "restaurant",
    "medical",
    "legal",
    "contractor",
    "consultant",
    "agency",
    "saas",
    "nonprofit",
    "general",
}

def select_template_name(
    profile: dict[str, Any],
) -> str:

    requested_template = str(
        profile.get(
            "template_name",
            "",
        )
    ).strip().lower()

    if requested_template in VALID_TEMPLATE_NAMES:
        return requested_template

    industry = str(
        profile.get(
            "industry",
            "general",
        )
    ).strip().lower()

    return INDUSTRY_TEMPLATE_MAP.get(
        industry,
        "modern",
    )

def select_layout_type(
    profile: dict[str, Any],
) -> str:

    requested_layout = str(
        profile.get(
            "layout_type",
            "",
        )
    ).strip().lower()

    if requested_layout in VALID_LAYOUT_TYPES:
        return requested_layout

    industry = str(
        profile.get(
            "industry",
            "general",
        )
    ).strip().lower()

    return INDUSTRY_LAYOUT_MAP.get(
        industry,
        "general",
    )

def infer_industry(
    profile: dict[str, Any],
) -> str:

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

    if _business_matches(
        business_type,
        "ecommerce",
        "shop",
        "store",
        "retail",
        "marketplace",
    ):
        return "ecommerce"

    if _business_matches(
        business_type,
        "restaurant",
        "cafe",
        "food",
        "pizza",
        "bakery",
    ):
        return "restaurant"

    if _business_matches(
        business_type,
        "doctor",
        "medical",
        "clinic",
        "hospital",
        "dentist",
        "health",
    ):
        return "medical"

    if _business_matches(
        business_type,
        "law",
        "lawyer",
        "legal",
        "attorney",
    ):
        return "legal"

    if _business_matches(
        business_type,
        "contractor",
        "roofing",
        "construction",
        "electrician",
        "plumber",
        "plumbing",
    ):
        return "contractor"

    if _business_matches(
        business_type,
        "consult",
        "coach",
        "advisor",
    ):
        return "consultant"

    if _business_matches(
        business_type,
        "agency",
        "marketing",
        "creative",
    ):
        return "agency"

    if _business_matches(
        business_type,
        "software",
        "saas",
        "platform",
        "application",
    ):
        return "saas"

    if _business_matches(
        business_type,
        "charity",
        "foundation",
        "nonprofit",
    ):
        return "nonprofit"

    return "general"

