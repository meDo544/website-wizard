from typing import Any


GATE_VERSION = "v1"
READINESS_THRESHOLD = 80


def _safe_score(value: Any) -> int:
    if isinstance(value, bool):
        return 0

    try:
        score = int(value)
    except (TypeError, ValueError):
        return 0

    return max(0, min(100, score))


def _gate_evidence(
    profile: dict[str, Any],
) -> dict[str, Any]:
    generation = profile.get("generation_evaluation", {})
    seo = profile.get("seo_readiness", {})
    accessibility = profile.get("accessibility_readiness", {})

    if not isinstance(generation, dict):
        generation = {}
    if not isinstance(seo, dict):
        seo = {}
    if not isinstance(accessibility, dict):
        accessibility = {}

    decision = generation.get("decision", "fail")
    if decision not in {"pass", "improve", "fail"}:
        decision = "fail"

    return {
        "generation_score": _safe_score(generation.get("score", 0)),
        "generation_decision": decision,
        "seo_score": _safe_score(seo.get("score", 0)),
        "accessibility_score": _safe_score(accessibility.get("score", 0)),
    }


def evaluate_generation_quality_gate(
    profile: dict[str, Any],
) -> dict[str, Any]:
    evidence = _gate_evidence(profile)

    blocking_dimensions: list[str] = []

    if (
        evidence["generation_decision"] != "pass"
        or evidence["generation_score"] < READINESS_THRESHOLD
    ):
        blocking_dimensions.append("generation")

    if evidence["seo_score"] < READINESS_THRESHOLD:
        blocking_dimensions.append("seo")

    if evidence["accessibility_score"] < READINESS_THRESHOLD:
        blocking_dimensions.append("accessibility")

    if not blocking_dimensions:
        decision = "pass"
    elif evidence["generation_decision"] == "fail":
        decision = "fail"
    else:
        decision = "review"

    reasons = [
        f"{name}_below_release_readiness"
        for name in blocking_dimensions
    ]

    return {
        "gate_version": GATE_VERSION,
        "decision": decision,
        "release_ready": decision == "pass",
        "evidence": evidence,
        "reasons": reasons,
        "blocking_dimensions": blocking_dimensions,
    }
