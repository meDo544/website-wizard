from typing import Any

from backend.services.scoring_calculator import (
    CONVERSION_SCORE_WEIGHTS,
    QUALITY_SCORE_WEIGHTS,
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

def evaluate_generation(
    profile: dict[str, Any],
) -> dict[str, Any]:
    conversion_max = sum(
        CONVERSION_SCORE_WEIGHTS.values()
    )
    dimensions = {
        "structural_completeness": (
            _evaluate_structural_completeness(
                profile
            )
        ),
        "conversion_readiness": _normalize_score(
            profile.get("conversion_score", 0),
            conversion_max,
        ),
        "content_quality": _evaluate_content_quality(
            profile
        ),
        "business_alignment": _presence_score(
            profile,
            (
                "industry",
                "template_name",
                "layout_type",
                "primary_goal",
            ),
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
