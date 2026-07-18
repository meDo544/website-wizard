from __future__ import annotations


GOAL_BY_INDUSTRY = {
    "consultant": "appointment_booking",
    "law_firm": "lead_generation",
    "medical": "appointment_booking",
    "ecommerce": "online_sales",
    "restaurant": "appointment_booking",
    "nonprofit": "donation",
    "church": "community_growth",
    "education": "education",
    "photographer": "lead_generation",
}


def infer_primary_goal(profile: dict) -> str:
    """
    Determine the business's primary conversion goal.
    """

    industry = profile.get("industry", "").lower()

    return GOAL_BY_INDUSTRY.get(
        industry,
        "lead_generation",
    )
