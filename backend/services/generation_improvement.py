from typing import Any

from backend.services.accessibility_readiness_evaluator import (
    evaluate_accessibility_readiness,
)
from backend.services.generation_evaluator import (
    evaluate_generation,
)
from backend.services.seo_readiness_evaluator import (
    evaluate_seo_readiness,
)


IMPROVEMENT_VERSION = "v1"


def _evaluation_snapshot(
    profile: dict[str, Any],
) -> dict[str, Any]:
    generation = profile.get(
        "generation_evaluation",
        {},
    )
    seo = profile.get(
        "seo_readiness",
        {},
    )
    accessibility = profile.get(
        "accessibility_readiness",
        {},
    )

    return {
        "generation_score": generation.get(
            "score",
            0,
        ),
        "generation_decision": generation.get(
            "decision",
            "fail",
        ),
        "seo_score": seo.get(
            "score",
            0,
        ),
        "accessibility_score": accessibility.get(
            "score",
            0,
        ),
    }


def _collect_improvement_targets(
    profile: dict[str, Any],
) -> list[str]:
    targets: list[str] = []

    sources = (
        (
            "generation",
            profile.get(
                "generation_evaluation",
                {},
            ),
        ),
        (
            "seo",
            profile.get(
                "seo_readiness",
                {},
            ),
        ),
        (
            "accessibility",
            profile.get(
                "accessibility_readiness",
                {},
            ),
        ),
    )

    for source_name, evaluation in sources:
        if not isinstance(evaluation, dict):
            continue

        source_targets = evaluation.get(
            "improvement_targets",
            [],
        )

        if not isinstance(source_targets, list):
            continue

        for target in source_targets:
            if not isinstance(target, str):
                continue

            target = target.strip()

            if not target:
                continue

            qualified_target = (
                f"{source_name}:{target}"
            )

            if qualified_target not in targets:
                targets.append(
                    qualified_target
                )

    return targets


def _repair_section_order(
    profile: dict[str, Any],
) -> bool:
    from backend.services.section_order_service import (
        DEFAULT_SECTION_ORDER,
        INDUSTRY_SECTION_RULES,
    )

    section_order = profile.get(
        "section_order",
        [],
    )

    recognized_sections = set(
        DEFAULT_SECTION_ORDER
    )

    valid_order = (
        isinstance(section_order, list)
        and bool(section_order)
        and len(section_order)
        == len(set(section_order))
        and all(
            isinstance(section, str)
            and section in recognized_sections
            for section in section_order
        )
    )

    if valid_order:
        return False

    industry = str(
        profile.get(
            "industry",
            "general",
        )
    ).strip().lower()

    canonical_order = (
        INDUSTRY_SECTION_RULES.get(
            industry,
            DEFAULT_SECTION_ORDER,
        )
    )

    profile["section_order"] = list(
        canonical_order
    )

    return True


def _reevaluate_profile(
    profile: dict[str, Any],
) -> None:
    profile["generation_evaluation"] = (
        evaluate_generation(profile)
    )
    profile["seo_readiness"] = (
        evaluate_seo_readiness(profile)
    )
    profile["accessibility_readiness"] = (
        evaluate_accessibility_readiness(
            profile
        )
    )


def _snapshot_improved(
    before: dict[str, Any],
    after: dict[str, Any],
) -> bool:
    return (
        after["generation_score"]
        > before["generation_score"]
        or after["seo_score"]
        > before["seo_score"]
        or after["accessibility_score"]
        > before["accessibility_score"]
    )


def build_generation_improvement(
    profile: dict[str, Any],
) -> dict[str, Any]:
    before = _evaluation_snapshot(
        profile
    )

    targets = _collect_improvement_targets(
        profile
    )

    requires_improvement = (
        before["generation_decision"]
        != "pass"
        or before["seo_score"] < 80
        or before["accessibility_score"] < 80
    )

    actions: list[str] = []

    structural_targets = {
        "generation:structural_completeness",
        "accessibility:structural_readiness",
    }

    should_repair_structure = bool(
        structural_targets.intersection(
            targets
        )
    )

    if (
        requires_improvement
        and should_repair_structure
        and _repair_section_order(profile)
    ):
        actions.append(
            "repair_section_order"
        )

    attempted = bool(actions)
    pass_count = 1 if attempted else 0

    if attempted:
        _reevaluate_profile(
            profile
        )

    after = _evaluation_snapshot(
        profile
    )

    improved = (
        attempted
        and _snapshot_improved(
            before,
            after,
        )
    )

    requires_improvement = (
        after["generation_decision"]
        != "pass"
        or after["seo_score"] < 80
        or after["accessibility_score"] < 80
    )

    return {
        "improvement_version": IMPROVEMENT_VERSION,
        "attempted": attempted,
        "pass_count": pass_count,
        "before": before,
        "targets": targets,
        "actions": actions,
        "after": after,
        "improved": improved,
        "requires_improvement": requires_improvement,
    }
