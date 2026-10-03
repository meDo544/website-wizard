from typing import Any


SEO_EVALUATION_VERSION = "v1"
TITLE_MIN_LENGTH = 30
TITLE_MAX_LENGTH = 65


def _meaningful_text(value: Any) -> str:
    if not isinstance(value, str):
        return ""

    return value.strip()


def _evaluate_metadata_presence(
    profile: dict[str, Any],
) -> int:
    fields = (
        "seo_title",
        "seo_description",
    )

    present = sum(
        1
        for field in fields
        if _meaningful_text(profile.get(field))
    )

    return round(
        present * 100 / len(fields)
    )


def _evaluate_metadata_quality(
    profile: dict[str, Any],
) -> int:
    title = _meaningful_text(
        profile.get("seo_title")
    )
    description = _meaningful_text(
        profile.get("seo_description")
    )

    title_quality = (
        100
        if TITLE_MIN_LENGTH <= len(title) <= TITLE_MAX_LENGTH
        else 0
    )

    description_quality = (
        100 if description else 0
    )

    return round(
        (title_quality + description_quality) / 2
    )


def _evaluate_content_discoverability(
    profile: dict[str, Any],
) -> int:
    identity = profile.get(
        "website_identity",
        {},
    )

    identity_business_name = (
        _meaningful_text(
            identity.get("business_name")
        )
        if isinstance(identity, dict)
        else ""
    )

    business_identity = bool(
        identity_business_name
        or _meaningful_text(
            profile.get("business_name")
        )
    )

    substantive_content = any(
        profile.get(field)
        for field in (
            "services",
            "features",
            "products",
            "testimonials",
            "faqs",
        )
    )

    descriptive_content = any(
        _meaningful_text(profile.get(field))
        for field in (
            "tagline",
            "about",
            "hero_title",
            "hero_subtitle",
        )
    )

    signals = (
        business_identity,
        substantive_content,
        descriptive_content,
    )

    return round(
        sum(100 for signal in signals if signal)
        / len(signals)
    )


def evaluate_seo_readiness(
    profile: dict[str, Any],
) -> dict[str, Any]:
    signals = {
        "metadata_presence": _evaluate_metadata_presence(profile),
        "metadata_quality": _evaluate_metadata_quality(profile),
        "content_discoverability": _evaluate_content_discoverability(profile),
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
        "evaluation_version": SEO_EVALUATION_VERSION,
        "score": score,
        "signals": signals,
        "findings": findings,
        "strengths": strengths,
        "improvement_targets": improvement_targets,
    }
