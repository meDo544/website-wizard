import pytest

from backend.services.generation_improvement import (
    IMPROVEMENT_VERSION,
    build_generation_improvement,
)


@pytest.mark.unit
def test_build_generation_improvement_for_passing_profile():
    profile = {
        "generation_evaluation": {
            "score": 90,
            "decision": "pass",
            "improvement_targets": [],
        },
        "seo_readiness": {
            "score": 85,
            "improvement_targets": [],
        },
        "accessibility_readiness": {
            "score": 80,
            "improvement_targets": [],
        },
    }

    result = build_generation_improvement(profile)

    assert result["improvement_version"] == IMPROVEMENT_VERSION
    assert result["attempted"] is False
    assert result["pass_count"] == 0
    assert result["targets"] == []
    assert result["actions"] == []
    assert result["improved"] is False
    assert result["requires_improvement"] is False
    assert result["before"] == {
        "generation_score": 90,
        "generation_decision": "pass",
        "seo_score": 85,
        "accessibility_score": 80,
    }
    assert result["after"] == result["before"]
    assert result["after"] is not result["before"]


@pytest.mark.unit
def test_build_generation_improvement_collects_namespaced_targets():
    profile = {
        "generation_evaluation": {
            "score": 72,
            "decision": "improve",
            "improvement_targets": [
                "structural_completeness",
                "content_quality",
            ],
        },
        "seo_readiness": {
            "score": 60,
            "improvement_targets": [
                "metadata_quality",
            ],
        },
        "accessibility_readiness": {
            "score": 67,
            "improvement_targets": [
                "structural_readiness",
            ],
        },
    }

    result = build_generation_improvement(profile)

    assert result["requires_improvement"] is True
    assert result["targets"] == [
        "generation:structural_completeness",
        "generation:content_quality",
        "seo:metadata_quality",
        "accessibility:structural_readiness",
    ]


@pytest.mark.unit
def test_build_generation_improvement_handles_missing_evaluations():
    result = build_generation_improvement({})

    assert result["before"] == {
        "generation_score": 0,
        "generation_decision": "fail",
        "seo_score": 0,
        "accessibility_score": 0,
    }
    assert result["targets"] == []
    assert result["requires_improvement"] is True


@pytest.mark.unit
def test_build_generation_improvement_ignores_invalid_targets():
    profile = {
        "generation_evaluation": {
            "score": 70,
            "decision": "improve",
            "improvement_targets": [
                "",
                None,
                123,
                " content_quality ",
                "content_quality",
            ],
        },
        "seo_readiness": {
            "score": 90,
            "improvement_targets": "metadata_quality",
        },
        "accessibility_readiness": {
            "score": 90,
            "improvement_targets": [],
        },
    }

    result = build_generation_improvement(profile)

    assert result["targets"] == [
        "generation:content_quality",
    ]


@pytest.mark.unit
def test_repair_section_order_repairs_invalid_order():
    from backend.services.generation_improvement import (
        _repair_section_order,
    )

    profile = {
        "industry": "restaurant",
        "section_order": [
            "bad",
            "bad",
        ],
    }

    changed = _repair_section_order(profile)

    assert changed is True
    assert profile["section_order"] == [
        "services",
        "features",
        "testimonials",
        "contact",
        "cta",
    ]


@pytest.mark.unit
def test_repair_section_order_preserves_valid_custom_order():
    from backend.services.generation_improvement import (
        _repair_section_order,
    )

    profile = {
        "industry": "restaurant",
        "section_order": [
            "services",
            "contact",
            "cta",
        ],
    }

    changed = _repair_section_order(profile)

    assert changed is False
    assert profile["section_order"] == [
        "services",
        "contact",
        "cta",
    ]


@pytest.mark.unit
def test_repair_section_order_uses_general_fallback():
    from backend.services.generation_improvement import (
        _repair_section_order,
    )
    from backend.services.section_order_service import (
        DEFAULT_SECTION_ORDER,
    )

    profile = {
        "industry": "unknown-industry",
        "section_order": [],
    }

    changed = _repair_section_order(profile)

    assert changed is True
    assert profile["section_order"] == DEFAULT_SECTION_ORDER
    assert profile["section_order"] is not DEFAULT_SECTION_ORDER


@pytest.mark.unit
def test_structural_target_repairs_invalid_order_once():
    profile = {
        "industry": "restaurant",
        "section_order": [
            "bad",
            "bad",
        ],
        "generation_evaluation": {
            "score": 70,
            "decision": "improve",
            "improvement_targets": [
                "structural_completeness",
            ],
        },
        "seo_readiness": {
            "score": 90,
            "improvement_targets": [],
        },
        "accessibility_readiness": {
            "score": 90,
            "improvement_targets": [],
        },
    }

    result = build_generation_improvement(profile)

    assert result["attempted"] is True
    assert result["pass_count"] == 1
    assert result["actions"] == [
        "repair_section_order",
    ]
    assert profile["section_order"] == [
        "services",
        "features",
        "testimonials",
        "contact",
        "cta",
    ]


@pytest.mark.unit
def test_structural_target_preserves_valid_order_without_attempt():
    profile = {
        "industry": "restaurant",
        "section_order": [
            "services",
            "contact",
            "cta",
        ],
        "generation_evaluation": {
            "score": 70,
            "decision": "improve",
            "improvement_targets": [
                "structural_completeness",
            ],
        },
        "seo_readiness": {
            "score": 90,
            "improvement_targets": [],
        },
        "accessibility_readiness": {
            "score": 90,
            "improvement_targets": [],
        },
    }

    result = build_generation_improvement(profile)

    assert result["attempted"] is False
    assert result["pass_count"] == 0
    assert result["actions"] == []
    assert profile["section_order"] == [
        "services",
        "contact",
        "cta",
    ]


@pytest.mark.unit
def test_unrelated_target_does_not_repair_invalid_order():
    original_order = [
        "bad",
        "bad",
    ]

    profile = {
        "industry": "restaurant",
        "section_order": original_order.copy(),
        "generation_evaluation": {
            "score": 70,
            "decision": "improve",
            "improvement_targets": [
                "content_quality",
            ],
        },
        "seo_readiness": {
            "score": 90,
            "improvement_targets": [],
        },
        "accessibility_readiness": {
            "score": 90,
            "improvement_targets": [],
        },
    }

    result = build_generation_improvement(profile)

    assert result["attempted"] is False
    assert result["pass_count"] == 0
    assert result["actions"] == []
    assert profile["section_order"] == original_order



@pytest.mark.unit
def test_real_evaluation_round_trip_improves_structural_readiness():
    from backend.services.accessibility_readiness_evaluator import (
        evaluate_accessibility_readiness,
    )
    from backend.services.generation_evaluator import (
        evaluate_generation,
    )
    from backend.services.seo_readiness_evaluator import (
        evaluate_seo_readiness,
    )

    profile = {
        "industry": "restaurant",
        "section_order": ["bad", "bad"],
        "services": ["Dining"],
        "features": ["Fresh menu"],
        "testimonials": ["Great experience"],
        "contact": {"email": "hello@example.com"},
        "cta": {"text": "Reserve a table"},
        "industry_components": [],
        "active_components": {},
    }

    profile["generation_evaluation"] = (
        evaluate_generation(profile)
    )
    profile["seo_readiness"] = (
        evaluate_seo_readiness(profile)
    )
    profile["accessibility_readiness"] = (
        evaluate_accessibility_readiness(profile)
    )

    result = build_generation_improvement(
        profile
    )

    assert result["attempted"] is True
    assert result["pass_count"] == 1
    assert result["actions"] == [
        "repair_section_order"
    ]
    assert result["improved"] is True
    assert (
        result["after"]["generation_score"]
        > result["before"]["generation_score"]
    )
    assert (
        result["after"]["accessibility_score"]
        > result["before"]["accessibility_score"]
    )
    assert (
        result["after"]["seo_score"]
        == result["before"]["seo_score"]
    )
    assert (
        profile["generation_evaluation"]
        ["dimensions"]
        ["structural_completeness"]
        == 100
    )
    assert (
        profile["accessibility_readiness"]
        ["signals"]
        ["structural_readiness"]
        == 100
    )
    assert profile["section_order"] == [
        "services",
        "features",
        "testimonials",
        "contact",
        "cta",
    ]
    assert result["requires_improvement"] is True
