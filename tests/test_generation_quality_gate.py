import pytest

from backend.services.generation_quality_gate import (
    GATE_VERSION,
    evaluate_generation_quality_gate,
)


@pytest.mark.unit
def test_quality_gate_passes_release_ready_profile():
    profile = {
        "generation_evaluation": {"score": 80, "decision": "pass"},
        "seo_readiness": {"score": 80},
        "accessibility_readiness": {"score": 80},
    }

    result = evaluate_generation_quality_gate(profile)

    assert result["gate_version"] == GATE_VERSION
    assert result["decision"] == "pass"
    assert result["release_ready"] is True
    assert result["blocking_dimensions"] == []
    assert result["reasons"] == []


@pytest.mark.unit
def test_quality_gate_reviews_improvable_generation():
    profile = {
        "generation_evaluation": {"score": 70, "decision": "improve"},
        "seo_readiness": {"score": 90},
        "accessibility_readiness": {"score": 90},
    }

    result = evaluate_generation_quality_gate(profile)

    assert result["decision"] == "review"
    assert result["release_ready"] is False
    assert result["blocking_dimensions"] == ["generation"]


@pytest.mark.unit
def test_quality_gate_reviews_readiness_deficiencies():
    profile = {
        "generation_evaluation": {"score": 90, "decision": "pass"},
        "seo_readiness": {"score": 79},
        "accessibility_readiness": {"score": 70},
    }

    result = evaluate_generation_quality_gate(profile)

    assert result["decision"] == "review"
    assert result["release_ready"] is False
    assert result["blocking_dimensions"] == [
        "seo",
        "accessibility",
    ]


@pytest.mark.unit
def test_quality_gate_fails_generation_failure():
    profile = {
        "generation_evaluation": {"score": 40, "decision": "fail"},
        "seo_readiness": {"score": 90},
        "accessibility_readiness": {"score": 90},
    }

    result = evaluate_generation_quality_gate(profile)

    assert result["decision"] == "fail"
    assert result["release_ready"] is False
    assert result["blocking_dimensions"] == ["generation"]


@pytest.mark.unit
def test_quality_gate_fails_closed_when_evidence_missing():
    result = evaluate_generation_quality_gate({})

    assert result["decision"] == "fail"
    assert result["release_ready"] is False
    assert result["evidence"] == {
        "generation_score": 0,
        "generation_decision": "fail",
        "seo_score": 0,
        "accessibility_score": 0,
    }
    assert result["blocking_dimensions"] == [
        "generation",
        "seo",
        "accessibility",
    ]


@pytest.mark.unit
def test_quality_gate_handles_malformed_evidence_defensively():
    profile = {
        "generation_evaluation": {
            "score": True,
            "decision": "unexpected",
        },
        "seo_readiness": {"score": "invalid"},
        "accessibility_readiness": None,
    }

    result = evaluate_generation_quality_gate(profile)

    assert result["decision"] == "fail"
    assert result["release_ready"] is False
    assert result["evidence"] == {
        "generation_score": 0,
        "generation_decision": "fail",
        "seo_score": 0,
        "accessibility_score": 0,
    }

@pytest.mark.unit
def test_quality_gate_is_attached_by_real_pipeline():
    from backend.services.website_intelligence_pipeline import (
        run_website_intelligence_pipeline,
    )

    profile = {
        "seo_title": "Fresh Handcrafted Pizza and Local Delivery",
        "seo_description": "Order handcrafted pizza made with fresh ingredients for convenient local delivery.",
        "services": ["Pizza Delivery", "Online Ordering"],
        "features": ["Fresh Ingredients", "Local Delivery"],
        "website_identity": {
            "business_name": "Test Pizza",
            "business_type": "Pizza Restaurant",
            "target_audience": "Local pizza customers",
        },
        "hero_variants": [
            {"type": "luxury", "title": "Fresh Pizza Made for You", "subtitle": "Order handcrafted pizza locally."}
        ],
        "cta_variants": [
            {"type": "booking", "text": "Order Online"}
        ],
        "offer_variants": [
            {"type": "discount", "headline": "Special Offer Today"}
        ],
        "social_proof_variants": [
            {"type": "local", "headline": "Trusted Locally"}
        ],
        "risk_reversal_variants": [
            {"type": "guarantee", "headline": "Satisfaction Guaranteed"}
        ],
        "urgency_variants": [
            {"type": "limited_time", "headline": "Order Today"}
        ],
        "objection_variants": [
            {"type": "convenience", "headline": "Easy Ordering"}
        ],
        "value_prop_variants": [
            {"type": "quality", "headline": "Fresh Ingredients"}
        ],
        "audience_variants": [
            {"type": "consumer", "headline": "For Pizza Lovers"}
        ],
        "differentiation_variants": [
            {"type": "quality", "headline": "Handcrafted Daily"}
        ],
        "emotional_trigger_variants": [
            {"type": "confidence", "headline": "Order With Confidence"}
        ],
        "buyer_motivation_variants": [
            {"type": "comfort", "headline": "Easy Dinner"}
        ],
        "pain_point_variants": [
            {"type": "time", "headline": "Skip Dinner Prep"}
        ],
        "outcome_variants": [
            {"type": "simplicity", "headline": "Dinner Made Simple"}
        ],
        "authority_variants": [
            {"type": "expertise", "headline": "Experienced Pizza Makers"}
        ],
        "industry_conversion_variants": [
            {"type": "restaurant", "headline": "Easy Local Ordering"}
        ],
    }

    result = run_website_intelligence_pipeline(profile)

    gate = result["generation_quality_gate"]
    evaluation = result["generation_evaluation"]
    seo = result["seo_readiness"]
    accessibility = result["accessibility_readiness"]

    assert gate["gate_version"] == GATE_VERSION
    assert gate["decision"] in {"pass", "review", "fail"}
    assert gate["release_ready"] is (
        gate["decision"] == "pass"
    )

    assert gate["evidence"] == {
        "generation_score": evaluation["score"],
        "generation_decision": evaluation["decision"],
        "seo_score": seo["score"],
        "accessibility_score": accessibility["score"],
    }

    assert set(gate["blocking_dimensions"]).issubset(
        {
            "generation",
            "seo",
            "accessibility",
        }
    )
