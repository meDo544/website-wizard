import pytest

from backend.core.metrics import (
    GENERATION_IMPROVEMENT_TOTAL,
    GENERATION_INTELLIGENCE_DURATION_SECONDS,
    GENERATION_QUALITY_GATE_TOTAL,
    GENERATION_READINESS_SCORE,
    record_generation_intelligence,
    track_generation_intelligence_duration,
)


def _sample_value(
    metric,
    sample_name,
    labels,
    *,
    default=None,
):
    for sample in metric.collect()[0].samples:
        if (
            sample.name == sample_name
            and sample.labels == labels
        ):
            return sample.value

    if default is not None:
        return default

    raise AssertionError(
        f"sample not found: {sample_name} {labels}"
    )


@pytest.mark.unit
def test_record_generation_intelligence_records_final_metrics():
    gate_before = _sample_value(
        GENERATION_QUALITY_GATE_TOTAL,
        "website_wizard_generation_quality_gate_total",
        {"decision": "pass"},
        default=0.0,
    )

    improvement_before = _sample_value(
        GENERATION_IMPROVEMENT_TOTAL,
        "website_wizard_generation_improvement_total",
        {
            "attempted": "true",
            "improved": "true",
        },
        default=0.0,
    )

    counts_before = {
        dimension: _sample_value(
            GENERATION_READINESS_SCORE,
            "website_wizard_generation_readiness_score_count",
            {"dimension": dimension},
            default=0.0,
        )
        for dimension in (
            "generation",
            "seo",
            "accessibility",
        )
    }

    sums_before = {
        dimension: _sample_value(
            GENERATION_READINESS_SCORE,
            "website_wizard_generation_readiness_score_sum",
            {"dimension": dimension},
            default=0.0,
        )
        for dimension in (
            "generation",
            "seo",
            "accessibility",
        )
    }

    record_generation_intelligence(
        gate_decision="pass",
        generation_score=88,
        seo_score=91,
        accessibility_score=84,
        improvement_attempted=True,
        improvement_improved=True,
    )

    assert _sample_value(
        GENERATION_QUALITY_GATE_TOTAL,
        "website_wizard_generation_quality_gate_total",
        {"decision": "pass"},
    ) == gate_before + 1

    assert _sample_value(
        GENERATION_IMPROVEMENT_TOTAL,
        "website_wizard_generation_improvement_total",
        {
            "attempted": "true",
            "improved": "true",
        },
    ) == improvement_before + 1

    expected_scores = {
        "generation": 88,
        "seo": 91,
        "accessibility": 84,
    }

    for dimension, expected_score in expected_scores.items():
        assert _sample_value(
            GENERATION_READINESS_SCORE,
            "website_wizard_generation_readiness_score_count",
            {"dimension": dimension},
        ) == counts_before[dimension] + 1

        assert _sample_value(
            GENERATION_READINESS_SCORE,
            "website_wizard_generation_readiness_score_sum",
            {"dimension": dimension},
        ) == sums_before[dimension] + expected_score


@pytest.mark.unit
def test_record_generation_intelligence_fails_closed_and_clamps_scores():
    fail_before = _sample_value(
        GENERATION_QUALITY_GATE_TOTAL,
        "website_wizard_generation_quality_gate_total",
        {"decision": "fail"},
        default=0.0,
    )

    improvement_before = _sample_value(
        GENERATION_IMPROVEMENT_TOTAL,
        "website_wizard_generation_improvement_total",
        {
            "attempted": "false",
            "improved": "false",
        },
        default=0.0,
    )

    sums_before = {
        dimension: _sample_value(
            GENERATION_READINESS_SCORE,
            "website_wizard_generation_readiness_score_sum",
            {"dimension": dimension},
            default=0.0,
        )
        for dimension in (
            "generation",
            "seo",
            "accessibility",
        )
    }

    record_generation_intelligence(
        gate_decision="unexpected",
        generation_score=150,
        seo_score=-10,
        accessibility_score="bad",
        improvement_attempted="true",
        improvement_improved="false",
    )

    assert _sample_value(
        GENERATION_QUALITY_GATE_TOTAL,
        "website_wizard_generation_quality_gate_total",
        {"decision": "fail"},
    ) == fail_before + 1

    assert _sample_value(
        GENERATION_IMPROVEMENT_TOTAL,
        "website_wizard_generation_improvement_total",
        {
            "attempted": "false",
            "improved": "false",
        },
    ) == improvement_before + 1

    assert _sample_value(
        GENERATION_READINESS_SCORE,
        "website_wizard_generation_readiness_score_sum",
        {"dimension": "generation"},
    ) == sums_before["generation"] + 100

    assert _sample_value(
        GENERATION_READINESS_SCORE,
        "website_wizard_generation_readiness_score_sum",
        {"dimension": "seo"},
    ) == sums_before["seo"]

    assert _sample_value(
        GENERATION_READINESS_SCORE,
        "website_wizard_generation_readiness_score_sum",
        {"dimension": "accessibility"},
    ) == sums_before["accessibility"]


@pytest.mark.unit
def test_track_generation_intelligence_duration_records_observation():
    count_before = _sample_value(
        GENERATION_INTELLIGENCE_DURATION_SECONDS,
        "website_wizard_generation_intelligence_duration_seconds_count",
        {},
    )

    with track_generation_intelligence_duration():
        pass

    count_after = _sample_value(
        GENERATION_INTELLIGENCE_DURATION_SECONDS,
        "website_wizard_generation_intelligence_duration_seconds_count",
        {},
    )

    assert count_after == count_before + 1
