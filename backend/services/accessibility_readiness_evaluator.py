from typing import Any


ACCESSIBILITY_EVALUATION_VERSION = "v1"

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


def _meaningful_text(value: Any) -> str:
    if not isinstance(value, str):
        return ""

    return value.strip()


def _evaluate_content_clarity(
    profile: dict[str, Any],
) -> int:
    hero_title = bool(
        _meaningful_text(profile.get("hero_title"))
    )
    hero_subtitle = bool(
        _meaningful_text(profile.get("hero_subtitle"))
    )
    supporting_content = any(
        profile.get(field)
        for field in (
            "about",
            "services",
            "features",
            "products",
            "faqs",
        )
    )

    signals = (
        hero_title,
        hero_subtitle,
        supporting_content,
    )

    return round(
        sum(100 for signal in signals if signal)
        / len(signals)
    )


def _evaluate_structural_readiness(
    profile: dict[str, Any],
) -> int:
    section_order = profile.get(
        "section_order",
        [],
    )

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

    if not valid_order:
        return 0

    populated = sum(
        1
        for section in section_order
        if profile.get(section)
    )

    coverage = round(
        populated * 100 / len(section_order)
    )

    return round(
        (100 + coverage) / 2
    )


def _evaluate_interaction_clarity(
    profile: dict[str, Any],
) -> int:
    identity = profile.get(
        "website_identity",
        {},
    )

    primary_cta = (
        _meaningful_text(
            identity.get("primary_cta")
        )
        if isinstance(identity, dict)
        else ""
    )

    cta = (
        primary_cta
        or _meaningful_text(profile.get("cta"))
    )

    contact = profile.get(
        "contact",
        {},
    )

    contact_available = (
        isinstance(contact, dict)
        and any(
            _meaningful_text(value)
            for value in contact.values()
        )
    )

    signals = (
        bool(cta),
        contact_available,
    )

    return round(
        sum(100 for signal in signals if signal)
        / len(signals)
    )


def evaluate_accessibility_readiness(
    profile: dict[str, Any],
) -> dict[str, Any]:
    signals = {
        "content_clarity": _evaluate_content_clarity(profile),
        "structural_readiness": _evaluate_structural_readiness(profile),
        "interaction_clarity": _evaluate_interaction_clarity(profile),
    }

    score = round(
        sum(signals.values()) / len(signals)
    )

    strengths = [
        name
        for name, value in signals.items()
        if value >= 80
    ]

    improvement_targets = [
        name
        for name, value in signals.items()
        if value < 80
    ]

    findings = [
        f"{name}: {value}"
        for name, value in signals.items()
        if value < 80
    ]

    return {
        "evaluation_version": ACCESSIBILITY_EVALUATION_VERSION,
        "score": score,
        "signals": signals,
        "findings": findings,
        "strengths": strengths,
        "improvement_targets": improvement_targets,
    }
