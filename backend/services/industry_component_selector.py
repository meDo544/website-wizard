from typing import Any


INDUSTRY_COMPONENTS = {

    "ecommerce": [
        "products",
        "shipping",
        "payments",
        "returns",
    ],

    "restaurant": [
        "menu",
        "reservations",
        "hours",
    ],

    "medical": [
        "treatments",
        "insurance",
        "appointments",
    ],

    "contractor": [
        "projects",
        "service_areas",
        "estimates",
    ],

    "consultant": [
        "case_studies",
        "process",
        "booking",
    ],

    "agency": [
        "portfolio",
        "case_studies",
        "process",
    ],

    "legal": [
        "practice_areas",
        "attorneys",
        "consultation",
    ],

    "saas": [
        "pricing",
        "integrations",
        "demo",
    ],

    "nonprofit": [
        "impact",
        "donate",
        "volunteer",
    ],

    "general": [],
}


def get_industry_components(
    profile: dict[str, Any],
) -> list[str]:

    industry = str(
        profile.get(
            "industry",
            "general",
        )
    ).lower()

    return list(
        INDUSTRY_COMPONENTS.get(
            industry,
            [],
        )
    )


def get_active_components(
    profile: dict[str, Any],
) -> dict[str, bool]:

    active = {
        component: True
        for component in get_industry_components(
            profile
        )
    }

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

    # Digital businesses generally don't require shipping/returns.
    if (
        "digital" in business_type
        or "software" in business_type
        or "download" in business_type
    ):
        active["shipping"] = False
        active["returns"] = False

    return active


def component_is_active(
    profile: dict[str, Any],
    component: str,
) -> bool:

    active_components = profile.get(
        "active_components",
        {},
    )

    if not isinstance(
        active_components,
        dict,
    ):
        return False

    return bool(
        active_components.get(
            component,
            False,
        )
    )
