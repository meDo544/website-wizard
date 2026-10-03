from typing import Any

from backend.services.scoring_calculator import (
    CONVERSION_SCORE_WEIGHTS,
    QUALITY_SCORE_WEIGHTS,
)
from backend.services.business_goal_selector import (
    GOAL_BY_INDUSTRY,
    infer_primary_goal,
)
from backend.services.business_profile_selector import (
    INDUSTRY_TEMPLATE_MAP,
    VALID_LAYOUT_TYPES,
    VALID_TEMPLATE_NAMES,
)
from backend.services.industry_component_selector import (
    get_active_components,
    get_industry_components,
)
from backend.services.industry_conversion_selector import (
    select_industry_conversion_variant,
)


EVALUATION_VERSION = "v1"
PASS_THRESHOLD = 80
IMPROVE_THRESHOLD = 50


def _normalize_score(
    value: Any,
    maximum: int,
) -> int:
    try:
        numeric_value = float(value)
    except (TypeError, ValueError):
        numeric_value = 0.0

    if maximum <= 0:
        return 0

    normalized = round(
        (numeric_value / maximum) * 100
    )

    return max(0, min(100, normalized))


def _presence_score(
    profile: dict[str, Any],
    fields: tuple[str, ...],
) -> int:
    present = sum(
        1
        for field in fields
        if profile.get(field)
    )

    return round(
        (present / len(fields)) * 100
    )


RECOGNIZED_SECTIONS = {
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
}


def _evaluate_structural_completeness(
    profile: dict[str, Any],
) -> int:
    section_order = profile.get("section_order", [])

    valid_order = (
        isinstance(section_order, list)
        and bool(section_order)
        and len(section_order) == len(set(section_order))
        and all(
            isinstance(section, str)
            and section in RECOGNIZED_SECTIONS
            for section in section_order
        )
    )
    order_score = 100 if valid_order else 0

    if isinstance(section_order, list) and section_order:
        covered = sum(
            1
            for section in section_order
            if profile.get(section)
        )
        coverage_score = round(
            (covered / len(section_order)) * 100
        )
    else:
        coverage_score = 0

    industry_components = profile.get(
        "industry_components",
        [],
    )
    active_components = profile.get(
        "active_components",
        {},
    )

    coherent_components = (
        "industry_components" in profile
        and "active_components" in profile
        and isinstance(industry_components, list)
        and isinstance(active_components, dict)
        and all(
            component in active_components
            and isinstance(active_components[component], bool)
            for component in industry_components
        )
    )
    component_score = (
        100 if coherent_components else 0
    )

    return round(
        (
            order_score
            + coverage_score
            + component_score
        ) / 3
    )


def _evaluate_content_quality(
    profile: dict[str, Any],
) -> int:
    core_fields = (
        "services",
        "features",
        "testimonials",
        "faqs",
        "contact",
        "cta",
    )

    completeness_score = _presence_score(
        profile,
        core_fields,
    )

    contact = profile.get("contact", {})
    populated_contact_fields = (
        sum(
            1
            for value in contact.values()
            if value
        )
        if isinstance(contact, dict)
        else 0
    )

    depth_checks = (
        isinstance(profile.get("services"), list)
        and len(profile["services"]) >= 2,
        isinstance(profile.get("features"), list)
        and len(profile["features"]) >= 2,
        isinstance(profile.get("testimonials"), list)
        and len(profile["testimonials"]) >= 2,
        isinstance(profile.get("faqs"), list)
        and len(profile["faqs"]) >= 2,
        populated_contact_fields >= 2,
        isinstance(profile.get("cta"), str)
        and bool(profile["cta"].strip()),
    )

    depth_score = round(
        (
            sum(depth_checks)
            / len(depth_checks)
        ) * 100
    )

    quality_max = sum(
        QUALITY_SCORE_WEIGHTS.values()
    )
    legacy_quality_score = _normalize_score(
        profile.get("quality_score", 0),
        quality_max,
    )

    return round(
        (
            completeness_score
            + depth_score
            + legacy_quality_score
        ) / 3
    )

def _evaluate_business_alignment(
    profile: dict[str, Any],
) -> int:
    industry = str(
        profile.get(
            "industry",
            "",
        )
    ).strip().lower()

    template_name = str(
        profile.get(
            "template_name",
            "",
        )
    ).strip().lower()

    layout_type = str(
        profile.get(
            "layout_type",
            "",
        )
    ).strip().lower()

    primary_goal = str(
        profile.get(
            "primary_goal",
            "",
        )
    ).strip().lower()

    valid_industries = set(
        INDUSTRY_TEMPLATE_MAP.keys()
    )

    valid_primary_goals = set(
        GOAL_BY_INDUSTRY.values()
    )
    valid_primary_goals.add(
        "lead_generation"
    )

    classification_valid = (
        industry in valid_industries
        and template_name in VALID_TEMPLATE_NAMES
        and layout_type in VALID_LAYOUT_TYPES
        and primary_goal in valid_primary_goals
    )

    expected_goal = infer_primary_goal(
        profile
    )

    goal_consistent = (
        primary_goal == expected_goal
    )

    expected_components = (
        get_industry_components(
            profile
        )
    )
    expected_active_components = (
        get_active_components(
            profile
        )
    )

    components_consistent = (
        profile.get(
            "industry_components"
        )
        == expected_components
        and profile.get(
            "active_components"
        )
        == expected_active_components
    )

    expected_conversion = (
        select_industry_conversion_variant(
            industry_conversion_variants=profile.get(
                "industry_conversion_variants",
                [],
            ),
            conversion_strategy=profile.get(
                "conversion_strategy",
                "general",
            ),
        )
    )

    conversion_consistent = (
        profile.get(
            "selected_industry_conversion_type"
        )
        == expected_conversion.get(
            "type"
        )
    )

    industry_intelligence_consistent = (
        components_consistent
        and conversion_consistent
    )

    signals = (
        classification_valid,
        goal_consistent,
        industry_intelligence_consistent,
    )

    return round(
        sum(
            100
            for signal in signals
            if signal
        )
        / len(signals)
    )


def _has_conversion_text(value: Any) -> bool:
    if not isinstance(value, dict):
        return False

    for field in ("headline", "subheadline", "subtitle", "text"):
        if str(value.get(field, "")).strip():
            return True

    return False


def _evaluate_conversion_readiness(
    profile: dict[str, Any],
) -> int:
    conversion_max = sum(
        CONVERSION_SCORE_WEIGHTS.values()
    )

    legacy_strength = _normalize_score(
        profile.get("conversion_score", 0),
        conversion_max,
    )

    core_objects = (
        "selected_hero",
        "selected_value_prop",
        "selected_offer",
        "selected_trust",
        "selected_social_proof",
        "selected_cta",
        "selected_objection",
        "selected_risk_reversal",
        "selected_urgency",
    )

    content_integrity = round(
        sum(
            100
            for field in core_objects
            if _has_conversion_text(
                profile.get(field)
            )
        )
        / len(core_objects)
    )

    coherence_pairs = (
        ("selected_hero", "selected_hero_type"),
        ("selected_value_prop", "selected_value_prop_type"),
        ("selected_offer", "selected_offer_type"),
        ("selected_trust", "selected_trust_type"),
        ("selected_social_proof", "selected_social_proof_type"),
        ("selected_cta", "selected_cta_type"),
        ("selected_objection", "selected_objection_type"),
        ("selected_risk_reversal", "selected_risk_reversal_type"),
        ("selected_urgency", "selected_urgency_type"),
    )

    coherent = 0

    for object_field, type_field in coherence_pairs:
        selected = profile.get(object_field)
        selected_type = str(
            profile.get(type_field, "")
        ).strip().lower()

        if not isinstance(selected, dict):
            continue

        object_type = str(
            selected.get("type", "")
        ).strip().lower()

        if object_type and object_type == selected_type:
            coherent += 1

    journey_coherence = round(
        coherent * 100 / len(coherence_pairs)
    )

    return round(
        (
            legacy_strength
            + content_integrity
            + journey_coherence
        )
        / 3
    )


def evaluate_generation(
    profile: dict[str, Any],
) -> dict[str, Any]:
    dimensions = {
        "structural_completeness": (
            _evaluate_structural_completeness(
                profile
            )
        ),
        "conversion_readiness": (
            _evaluate_conversion_readiness(
                profile
            )
        ),
        "content_quality": _evaluate_content_quality(
            profile
        ),
        "business_alignment": _evaluate_business_alignment(
            profile
        ),
    }

    score = round(
        sum(dimensions.values())
        / len(dimensions)
    )

    if score >= PASS_THRESHOLD:
        decision = "pass"
    elif score >= IMPROVE_THRESHOLD:
        decision = "improve"
    else:
        decision = "fail"

    strengths = [
        name
        for name, value in dimensions.items()
        if value >= PASS_THRESHOLD
    ]

    improvement_targets = [
        name
        for name, value in dimensions.items()
        if value < PASS_THRESHOLD
    ]

    findings = [
        f"{name}={value}"
        for name, value in dimensions.items()
    ]

    return {
        "evaluation_version": EVALUATION_VERSION,
        "score": score,
        "decision": decision,
        "requires_improvement": decision != "pass",
        "dimensions": dimensions,
        "findings": findings,
        "strengths": strengths,
        "improvement_targets": improvement_targets,
    }
