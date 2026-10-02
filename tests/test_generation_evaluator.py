import pytest

from backend.services.generation_evaluator import (
    evaluate_generation,
)


@pytest.mark.unit
def test_generation_evaluation_contract():
    profile = {
        "industry": "ecommerce",
        "template_name": "modern",
        "layout_type": "general",
        "primary_goal": "lead_generation",
        "section_order": ["hero", "products", "trust", "cta"],
        "conversion_strategy": {"type": "ecommerce"},
        "industry_components": {"components": ["products", "trust"]},
        "active_components": ["products", "trust"],
        "conversion_score": 125,
        "quality_score": 88,
        "conversion_score_breakdown": {"hero": 10, "cta": 10},
        "quality_score_breakdown": {"hero": 10, "cta": 10},
    }

    result = evaluate_generation(profile)

    assert result["evaluation_version"] == "v1"
    assert result["decision"] in {"pass", "improve", "fail"}
    assert isinstance(result["requires_improvement"], bool)
    assert 0 <= result["score"] <= 100

    assert set(result["dimensions"]) == {
        "structural_completeness",
        "conversion_readiness",
        "content_quality",
        "business_alignment",
    }

    for dimension in result["dimensions"].values():
        assert 0 <= dimension <= 100

    assert isinstance(result["findings"], list)
    assert isinstance(result["strengths"], list)
    assert isinstance(result["improvement_targets"], list)


@pytest.mark.unit
def test_generation_evaluation_normalizes_legacy_scores():
    profile = {
        "conversion_score": 125,
        "quality_score": 88,
    }

    result = evaluate_generation(profile)

    assert result["dimensions"]["conversion_readiness"] == 100
    assert result["dimensions"]["content_quality"] == 100


@pytest.mark.unit
def test_generation_evaluation_is_bounded_for_out_of_range_scores():
    profile = {
        "conversion_score": 999,
        "quality_score": 999,
    }

    result = evaluate_generation(profile)

    assert result["dimensions"]["conversion_readiness"] == 100
    assert result["dimensions"]["content_quality"] == 100
    assert 0 <= result["score"] <= 100


@pytest.mark.unit
def test_generation_evaluation_passes_strong_profile():
    profile = {
        "industry": "ecommerce",
        "template_name": "modern",
        "layout_type": "general",
        "primary_goal": "lead_generation",
        "section_order": ["hero", "products", "trust", "cta"],
        "industry_components": {"components": ["products"]},
        "active_components": ["products"],
        "conversion_score": 125,
        "quality_score": 88,
    }

    result = evaluate_generation(profile)

    assert result["score"] == 100
    assert result["decision"] == "pass"
    assert result["requires_improvement"] is False
    assert result["improvement_targets"] == []


@pytest.mark.unit
def test_generation_evaluation_improves_partial_profile():
    profile = {
        "industry": "ecommerce",
        "template_name": "modern",
        "layout_type": "general",
        "primary_goal": "lead_generation",
        "conversion_score": 125,
        "quality_score": 88,
    }

    result = evaluate_generation(profile)

    assert result["score"] == 75
    assert result["decision"] == "improve"
    assert result["requires_improvement"] is True
    assert "structural_completeness" in result["improvement_targets"]


@pytest.mark.unit
def test_generation_evaluation_fails_empty_profile():
    result = evaluate_generation({})

    assert result["score"] == 0
    assert result["decision"] == "fail"
    assert result["requires_improvement"] is True
    assert set(result["improvement_targets"]) == {
        "structural_completeness",
        "conversion_readiness",
        "content_quality",
        "business_alignment",
    }

@pytest.mark.unit
def test_generation_evaluation_is_attached_by_real_pipeline():
    from backend.services.website_intelligence_pipeline import (
        run_website_intelligence_pipeline,
    )

    profile = {
        "website_identity": {
            "business_name": "Test Pizza",
            "business_type": "Pizza Restaurant",
            "target_audience": "Local pizza customers",
        },
        "hero_variants": [
            {
                "type": "luxury",
                "title": "Fresh Pizza Made for You",
                "subtitle": "Order handcrafted pizza locally.",
            }
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
    evaluation = result["generation_evaluation"]

    assert result["industry"] == "restaurant"
    assert result["template_name"] == "luxury"
    assert result["layout_type"] == "visual"
    assert result["primary_goal"] == "appointment_booking"

    assert evaluation["evaluation_version"] == "v1"
    assert evaluation["decision"] in {"pass", "improve", "fail"}
    assert 0 <= evaluation["score"] <= 100
    assert set(evaluation["dimensions"]) == {
        "structural_completeness",
        "conversion_readiness",
        "content_quality",
        "business_alignment",
    }
