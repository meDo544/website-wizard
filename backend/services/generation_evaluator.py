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


def evaluate_generation(
    profile: dict[str, Any],
) -> dict[str, Any]:
    conversion_max = sum(
        CONVERSION_SCORE_WEIGHTS.values()
    )
    quality_max = sum(
        QUALITY_SCORE_WEIGHTS.values()
    )

    dimensions = {
        "structural_completeness": _presence_score(
            profile,
            (
                "section_order",
                "industry_components",
                "active_components",
            ),
        ),
        "conversion_readiness": _normalize_score(
            profile.get("conversion_score", 0),
            conversion_max,
        ),
        "content_quality": _normalize_score(
            profile.get("quality_score", 0),
            quality_max,
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
