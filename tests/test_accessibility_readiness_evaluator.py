import pytest

from backend.services.accessibility_readiness_evaluator import (
    evaluate_accessibility_readiness,
)


@pytest.mark.unit
def test_complete_accessibility_readiness_scores_100():
    profile = {
        "hero_title": "Build Better Websites",
        "hero_subtitle": "A clear description of the service.",
        "about": "Helpful supporting information.",
        "services": ["Design", "Development"],
        "features": ["Fast", "Reliable"],
        "faqs": [{"question": "How?", "answer": "Carefully."}],
        "contact": {
            "email": "hello@example.com",
            "phone": "555-0100",
        },
        "cta": "Get Started",
        "website_identity": {
            "primary_cta": "Get Started",
        },
        "section_order": [
            "services",
            "features",
            "faqs",
            "contact",
            "cta",
        ],
    }

    result = evaluate_accessibility_readiness(profile)

    assert result["evaluation_version"] == "v1"
    assert result["score"] == 100
    assert result["signals"] == {
        "content_clarity": 100,
        "structural_readiness": 100,
        "interaction_clarity": 100,
    }
    assert result["improvement_targets"] == []


@pytest.mark.unit
def test_content_clarity_requires_meaningful_profile_content():
    result = evaluate_accessibility_readiness(
        {
            "hero_title": "Clear title",
            "hero_subtitle": "",
        }
    )

    assert result["signals"]["content_clarity"] == 33


@pytest.mark.unit
def test_structural_readiness_scores_order_and_coverage():
    result = evaluate_accessibility_readiness(
        {
            "services": ["One service"],
            "section_order": [
                "services",
                "features",
            ],
        }
    )

    assert result["signals"]["structural_readiness"] == 75


@pytest.mark.unit
def test_invalid_section_order_scores_zero():
    result = evaluate_accessibility_readiness(
        {
            "services": ["One service"],
            "section_order": [
                "services",
                "services",
            ],
        }
    )

    assert result["signals"]["structural_readiness"] == 0


@pytest.mark.unit
def test_interaction_clarity_accepts_primary_cta_and_contact():
    result = evaluate_accessibility_readiness(
        {
            "website_identity": {
                "primary_cta": "Book Now",
            },
            "contact": {
                "email": "hello@example.com",
            },
        }
    )

    assert result["signals"]["interaction_clarity"] == 100


@pytest.mark.unit
def test_non_string_interaction_values_do_not_count_as_text():
    result = evaluate_accessibility_readiness(
        {
            "website_identity": {
                "primary_cta": None,
            },
            "cta": 123,
            "contact": {
                "email": None,
                "phone": False,
            },
        }
    )

    assert result["signals"]["interaction_clarity"] == 0


@pytest.mark.unit
def test_empty_profile_scores_zero():
    result = evaluate_accessibility_readiness({})

    assert result["score"] == 0
    assert result["signals"] == {
        "content_clarity": 0,
        "structural_readiness": 0,
        "interaction_clarity": 0,
    }
    assert set(result["improvement_targets"]) == {
        "content_clarity",
        "structural_readiness",
        "interaction_clarity",
    }
