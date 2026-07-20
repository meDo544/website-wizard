"""
Business profile classification.

This module centralizes deterministic business classification so the
website generation pipeline has a single entry point for assigning
derived profile attributes.
"""

from backend.services.business_goal_selector import (
    infer_primary_goal,
)

from backend.services.business_profile_selector import (
    infer_industry,
    select_layout_type,
    select_template_name,
)


def classify_business_profile(profile: dict) -> dict:
    """
    Populate deterministic business profile fields.

    Adds or updates:
        - industry
        - template_name
        - layout_type
        - primary_goal

    Returns the updated profile dictionary.
    """

    profile["industry"] = infer_industry(profile)
    profile["template_name"] = select_template_name(profile)
    profile["layout_type"] = select_layout_type(profile)
    profile["primary_goal"] = infer_primary_goal(profile)

    return profile
