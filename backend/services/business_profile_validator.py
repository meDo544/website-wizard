from backend.services.business_goal_selector import GOAL_BY_INDUSTRY
from backend.services.business_profile_selector import (
    VALID_TEMPLATE_NAMES,
    VALID_LAYOUT_TYPES,
    INDUSTRY_TEMPLATE_MAP,
)

VALID_INDUSTRIES = set(INDUSTRY_TEMPLATE_MAP.keys())
VALID_PRIMARY_GOALS = set(GOAL_BY_INDUSTRY.values())
VALID_TEMPLATES = set(VALID_TEMPLATE_NAMES)
VALID_LAYOUTS = set(VALID_LAYOUT_TYPES)

REQUIRED_FIELDS = (
    "industry",
    "template_name",
    "layout_type",
    "primary_goal",
)

def validate_business_profile(profile: dict) -> None:
    if not isinstance(profile, dict):
        raise TypeError(
            f"Expected profile to be a dict, got {type(profile).__name__}"
        )

    ...

    if profile["industry"] not in VALID_INDUSTRIES:
        raise ValueError(
            f"Invalid industry: {profile['industry']}"
        )

    if profile["template_name"] not in VALID_TEMPLATES:
        raise ValueError(
            f"Invalid template_name: {profile['template_name']}"
        )

    if profile["layout_type"] not in VALID_LAYOUTS:
        raise ValueError(
            f"Invalid layout_type: {profile['layout_type']}"
        )

    if profile["primary_goal"] not in VALID_PRIMARY_GOALS:
        raise ValueError(
            f"Invalid primary_goal: {profile['primary_goal']}"
        )


