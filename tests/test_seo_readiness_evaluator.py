import pytest

from backend.services.seo_readiness_evaluator import (
    _evaluate_content_discoverability,
    _evaluate_metadata_presence,
    _evaluate_metadata_quality,
    evaluate_seo_readiness,
)


@pytest.mark.unit
def test_seo_readiness_scores_complete_profile():
    profile = {
        "seo_title": "Professional Web Design for Growing Businesses",
        "seo_description": "Custom websites built for growing businesses.",
        "website_identity": {
            "business_name": "Example Studio",
        },
        "services": ["Web Design", "SEO"],
        "hero_title": "Build a Better Website",
    }

    result = evaluate_seo_readiness(profile)

    assert result["evaluation_version"] == "v1"
    assert result["score"] == 100
    assert result["signals"] == {
        "metadata_presence": 100,
        "metadata_quality": 100,
        "content_discoverability": 100,
    }
    assert set(result["strengths"]) == {
        "metadata_presence",
        "metadata_quality",
        "content_discoverability",
    }
    assert result["improvement_targets"] == []
    assert result["findings"] == []


@pytest.mark.unit
def test_metadata_presence_requires_both_fields():
    profile = {
        "seo_title": "Professional Web Design Services",
        "seo_description": "",
    }

    assert _evaluate_metadata_presence(profile) == 50


@pytest.mark.unit
def test_metadata_quality_enforces_existing_title_range():
    profile = {
        "seo_title": "Too short",
        "seo_description": "A useful description.",
    }

    assert _evaluate_metadata_quality(profile) == 50


@pytest.mark.unit
def test_content_discoverability_uses_profile_content():
    profile = {
        "business_name": "Example Studio",
        "features": ["Fast", "Reliable"],
        "tagline": "Websites that help businesses grow.",
    }

    assert _evaluate_content_discoverability(profile) == 100


@pytest.mark.unit
def test_seo_readiness_handles_empty_profile():
    result = evaluate_seo_readiness({})

    assert result["score"] == 0
    assert result["signals"] == {
        "metadata_presence": 0,
        "metadata_quality": 0,
        "content_discoverability": 0,
    }
    assert result["strengths"] == []
    assert set(result["improvement_targets"]) == {
        "metadata_presence",
        "metadata_quality",
        "content_discoverability",
    }


@pytest.mark.unit
def test_non_string_metadata_does_not_count_as_text():
    profile = {
        "seo_title": None,
        "seo_description": 123,
    }

    assert _evaluate_metadata_presence(profile) == 0
    assert _evaluate_metadata_quality(profile) == 0
