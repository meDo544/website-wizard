import pytest

from backend.services.generation_evaluator import (
    _evaluate_business_alignment,
    _evaluate_content_quality,
    _evaluate_conversion_readiness,
    _evaluate_structural_completeness,
    evaluate_generation,
)


def _complete_conversion_journey() -> dict:
    return {
        "selected_hero": {
            "type": "benefit",
            "headline": "Build Better",
            "subheadline": "A clear reason to act.",
        },
        "selected_hero_type": "benefit",
        "selected_value_prop": {
            "type": "quality",
            "headline": "Built for Results",
        },
        "selected_value_prop_type": "quality",
        "selected_offer": {
            "type": "discount",
            "headline": "Special Offer",
        },
        "selected_offer_type": "discount",
        "selected_trust": {
            "type": "reviews",
            "headline": "Trusted by Customers",
        },
        "selected_trust_type": "reviews",
        "selected_social_proof": {
            "type": "reviews",
            "headline": "Customers Recommend Us",
        },
        "selected_social_proof_type": "reviews",
        "selected_cta": {
            "type": "purchase",
            "text": "Shop Now",
        },
        "selected_cta_type": "purchase",
        "selected_objection": {
            "type": "convenience",
            "headline": "Simple and Easy",
        },
        "selected_objection_type": "convenience",
        "selected_risk_reversal": {
            "type": "guarantee",
            "headline": "Satisfaction Guaranteed",
        },
        "selected_risk_reversal_type": "guarantee",
        "selected_urgency": {
            "type": "limited_stock",
            "headline": "Available Today",
        },
        "selected_urgency_type": "limited_stock",
    }


@pytest.mark.unit
def test_conversion_readiness_scores_complete_coherent_journey():
    profile = _complete_conversion_journey()
    profile["conversion_score"] = 125

    assert _evaluate_conversion_readiness(profile) == 100


@pytest.mark.unit
def test_conversion_readiness_penalizes_missing_conversion_content():
    profile = _complete_conversion_journey()
    profile["conversion_score"] = 125

    for field in (
        "selected_hero",
        "selected_value_prop",
        "selected_offer",
        "selected_trust",
        "selected_social_proof",
        "selected_cta",
        "selected_objection",
        "selected_risk_reversal",
        "selected_urgency",
    ):
        profile[field] = {
            "type": profile[field]["type"]
        }

    assert _evaluate_conversion_readiness(profile) == 67


@pytest.mark.unit
def test_conversion_readiness_penalizes_incoherent_selected_types():
    profile = _complete_conversion_journey()
    profile["conversion_score"] = 125

    for field in (
        "selected_hero_type",
        "selected_value_prop_type",
        "selected_offer_type",
        "selected_trust_type",
        "selected_social_proof_type",
        "selected_cta_type",
        "selected_objection_type",
        "selected_risk_reversal_type",
        "selected_urgency_type",
    ):
        profile[field] = "mismatch"

    assert _evaluate_conversion_readiness(profile) == 67


@pytest.mark.unit
def test_business_alignment_scores_fully_aligned_ecommerce_profile():
    profile = {
        "industry": "ecommerce",
        "template_name": "modern",
        "layout_type": "catalog",
        "primary_goal": "online_sales",
        "conversion_strategy": "ecommerce",
        "website_identity": {
            "business_type": "Ecommerce Store",
        },
        "industry_components": [
            "products",
            "shipping",
            "payments",
            "returns",
        ],
        "active_components": {
            "products": True,
            "shipping": True,
            "payments": True,
            "returns": True,
        },
        "industry_conversion_variants": [
            {
                "type": "ecommerce",
                "headline": "Built for Online Stores",
            },
        ],
        "selected_industry_conversion_type": "ecommerce",
    }

    assert _evaluate_business_alignment(profile) == 100


@pytest.mark.unit
def test_business_alignment_accepts_valid_explicit_template_and_layout():
    profile = {
        "industry": "ecommerce",
        "template_name": "classic",
        "layout_type": "authority",
        "primary_goal": "online_sales",
        "conversion_strategy": "ecommerce",
        "website_identity": {
            "business_type": "Ecommerce Store",
        },
        "industry_components": [
            "products",
            "shipping",
            "payments",
            "returns",
        ],
        "active_components": {
            "products": True,
            "shipping": True,
            "payments": True,
            "returns": True,
        },
        "industry_conversion_variants": [
            {
                "type": "ecommerce",
                "headline": "Built for Online Stores",
            },
        ],
        "selected_industry_conversion_type": "ecommerce",
    }

    assert _evaluate_business_alignment(profile) == 100


@pytest.mark.unit
def test_business_alignment_penalizes_inconsistent_primary_goal():
    profile = {
        "industry": "ecommerce",
        "template_name": "modern",
        "layout_type": "catalog",
        "primary_goal": "lead_generation",
        "conversion_strategy": "ecommerce",
        "website_identity": {
            "business_type": "Ecommerce Store",
        },
        "industry_components": [
            "products",
            "shipping",
            "payments",
            "returns",
        ],
        "active_components": {
            "products": True,
            "shipping": True,
            "payments": True,
            "returns": True,
        },
        "industry_conversion_variants": [
            {
                "type": "ecommerce",
                "headline": "Built for Online Stores",
            },
        ],
        "selected_industry_conversion_type": "ecommerce",
    }

    assert _evaluate_business_alignment(profile) == 67


@pytest.mark.unit
def test_business_alignment_penalizes_misaligned_industry_intelligence():
    profile = {
        "industry": "ecommerce",
        "template_name": "modern",
        "layout_type": "catalog",
        "primary_goal": "online_sales",
        "conversion_strategy": "ecommerce",
        "website_identity": {
            "business_type": "Ecommerce Store",
        },
        "industry_components": [
            "menu",
            "reservations",
            "hours",
        ],
        "active_components": {
            "menu": True,
            "reservations": True,
            "hours": True,
        },
        "industry_conversion_variants": [
            {
                "type": "restaurant",
                "headline": "Built for Restaurants",
            },
            {
                "type": "ecommerce",
                "headline": "Built for Online Stores",
            },
        ],
        "selected_industry_conversion_type": "restaurant",
    }

    assert _evaluate_business_alignment(profile) == 67


@pytest.mark.unit
def test_generation_evaluation_contract():
    profile = {
        "industry": "ecommerce",
        "template_name": "modern",
        "layout_type": "general",
        "primary_goal": "lead_generation",
        "section_order": ["hero", "products", "trust", "cta"],
        "conversion_strategy": {"type": "ecommerce"},
        "industry_components": ["products", "shipping", "payments", "returns"],
        "active_components": {"products": True, "shipping": True, "payments": True, "returns": True},
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

    assert result["dimensions"]["conversion_readiness"] == 33
    assert result["dimensions"]["content_quality"] == 33


@pytest.mark.unit
def test_generation_evaluation_is_bounded_for_out_of_range_scores():
    profile = {
        "conversion_score": 999,
        "quality_score": 999,
    }

    result = evaluate_generation(profile)

    assert result["dimensions"]["conversion_readiness"] == 33
    assert result["dimensions"]["content_quality"] == 33
    assert 0 <= result["score"] <= 100


@pytest.mark.unit
def test_generation_evaluation_passes_strong_profile():
    profile = {
        "industry": "ecommerce",
        "template_name": "modern",
        "layout_type": "general",
        "primary_goal": "online_sales",
        "conversion_strategy": "ecommerce",
        "website_identity": {
            "business_type": "Ecommerce Store",
        },
        "section_order": ["services", "features", "testimonials", "faqs", "contact", "cta"],
        "services": ["Web Design", "SEO"],
        "features": ["Fast", "Secure"],
        "testimonials": [
            {"name": "A", "quote": "Excellent"},
            {"name": "B", "quote": "Reliable"},
        ],
        "faqs": [
            {"question": "How?", "answer": "Simply."},
            {"question": "When?", "answer": "Today."},
        ],
        "contact": {
            "email": "hello@example.com",
            "phone": "555-0100",
        },
        "cta": "Get Started",
        "industry_components": [
            "products",
            "shipping",
            "payments",
            "returns",
        ],
        "active_components": {
            "products": True,
            "shipping": True,
            "payments": True,
            "returns": True,
        },
        "industry_conversion_variants": [
            {
                "type": "ecommerce",
                "headline": "Built for Online Stores",
            },
        ],
        "selected_industry_conversion_type": "ecommerce",
        "conversion_score": 125,
        "quality_score": 88,
        **_complete_conversion_journey(),
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
        "primary_goal": "online_sales",
        "conversion_strategy": "ecommerce",
        "website_identity": {
            "business_type": "Ecommerce Store",
        },
        "industry_components": [
            "products",
            "shipping",
            "payments",
            "returns",
        ],
        "active_components": {
            "products": True,
            "shipping": True,
            "payments": True,
            "returns": True,
        },
        "industry_conversion_variants": [
            {
                "type": "ecommerce",
                "headline": "Built for Online Stores",
            },
        ],
        "selected_industry_conversion_type": "ecommerce",
        "conversion_score": 125,
        "quality_score": 88,
        **_complete_conversion_journey(),
    }

    result = evaluate_generation(profile)

    assert result["score"] == 66
    assert result["decision"] == "improve"
    assert result["requires_improvement"] is True
    assert set(result["improvement_targets"]) == {
        "structural_completeness",
        "content_quality",
    }


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
    assert evaluation["dimensions"]["business_alignment"] == 100


@pytest.mark.unit
def test_structural_completeness_scores_complete_profile():
    profile = {
        "section_order": ["services", "features", "testimonials", "faqs", "contact", "cta"],
        "services": ["Web Design"],
        "features": ["Fast Delivery"],
        "testimonials": [{"name": "Customer", "quote": "Excellent service"}],
        "faqs": [{"question": "How?", "answer": "We make it simple."}],
        "contact": {"email": "hello@example.com"},
        "cta": "Get Started",
        "industry_components": [],
        "active_components": {},
    }

    assert _evaluate_structural_completeness(profile) == 100


@pytest.mark.unit
def test_structural_completeness_detects_missing_section_content():
    profile = {
        "section_order": ["services", "features", "testimonials", "faqs", "contact", "cta"],
        "services": ["Web Design"],
        "features": [],
        "testimonials": [],
        "faqs": [],
        "contact": {},
        "cta": "",
        "industry_components": [],
        "active_components": {},
    }

    assert _evaluate_structural_completeness(profile) == 72


@pytest.mark.unit
def test_structural_completeness_detects_incoherent_components():
    profile = {
        "section_order": ["products", "shipping", "payments", "returns", "cta"],
        "products": [{"name": "Product", "description": "Useful product"}],
        "shipping": {"headline": "Shipping", "description": "Fast delivery"},
        "payments": {"headline": "Payments", "description": "Secure checkout"},
        "returns": {"headline": "Returns", "description": "Easy returns"},
        "cta": "Shop Now",
        "industry_components": ["products", "shipping", "payments", "returns"],
        "active_components": {"products": True, "shipping": True},
    }

    assert _evaluate_structural_completeness(profile) == 67


@pytest.mark.unit
def test_content_quality_scores_complete_deep_content():
    profile = {
        "services": ["Web Design", "SEO"],
        "features": ["Fast", "Secure"],
        "testimonials": [
            {"name": "A", "quote": "Excellent"},
            {"name": "B", "quote": "Reliable"},
        ],
        "faqs": [
            {"question": "How?", "answer": "Simply."},
            {"question": "When?", "answer": "Today."},
        ],
        "contact": {
            "email": "hello@example.com",
            "phone": "555-0100",
        },
        "cta": "Get Started",
        "quality_score": 88,
    }

    assert _evaluate_content_quality(profile) == 100


@pytest.mark.unit
def test_content_quality_detects_shallow_content():
    profile = {
        "services": ["Web Design"],
        "features": ["Fast"],
        "testimonials": [
            {"name": "A", "quote": "Excellent"},
        ],
        "faqs": [
            {"question": "How?", "answer": "Simply."},
        ],
        "contact": {
            "email": "hello@example.com",
        },
        "cta": "Get Started",
        "quality_score": 88,
    }

    assert _evaluate_content_quality(profile) == 72


@pytest.mark.unit
def test_content_quality_does_not_rely_only_on_legacy_score():
    profile = {
        "quality_score": 88,
    }

    assert _evaluate_content_quality(profile) == 33
