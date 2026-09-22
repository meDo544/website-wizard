from typing import Any


CONVERSION_SCORE_FIELDS = [
    "selected_hero_type",
    "selected_cta_type",
    "selected_offer_type",
    "selected_trust_type",
    "selected_social_proof_type",
    "selected_risk_reversal_type",
    "selected_urgency_type",
    "selected_objection_type",
    "selected_value_prop_type",
    "selected_audience_type",
    "selected_differentiation_type",
    "selected_emotional_trigger_type",
    "selected_buyer_motivation_type",
    "selected_pain_point_type",
    "selected_outcome_type",
    "selected_authority_type",
    "selected_industry_conversion_type",
]


CONVERSION_SCORE_WEIGHTS = {
    "selected_hero_type": 10,
    "selected_cta_type": 10,
    "selected_offer_type": 8,
    "selected_trust_type": 8,
    "selected_social_proof_type": 7,
    "selected_risk_reversal_type": 7,
    "selected_urgency_type": 7,
    "selected_objection_type": 7,
    "selected_value_prop_type": 10,
    "selected_audience_type": 6,
    "selected_differentiation_type": 7,
    "selected_emotional_trigger_type": 6,
    "selected_buyer_motivation_type": 6,
    "selected_pain_point_type": 6,
    "selected_outcome_type": 8,
    "selected_authority_type": 7,
    "selected_industry_conversion_type": 5,
}


QUALITY_SCORE_WEIGHTS = {
    "hero_quality": 10,
    "cta_quality": 10,
    "offer_quality": 8,
    "trust_quality": 8,
    "emotional_impact": 8,
    "clarity": 10,
    "specificity": 10,
    "authority_quality": 8,
    "urgency_quality": 6,
    "outcome_quality": 10,
}


QUALITY_KEYWORDS = {
    "clarity": [
        "easy",
        "simple",
        "clear",
        "fast",
        "trusted",
        "secure",
        "proven",
    ],
    "specificity": [
        "free",
        "custom",
        "personalized",
        "local",
        "premium",
        "expert",
        "guarantee",
    ],
    "emotional": [
        "confidence",
        "success",
        "growth",
        "secure",
        "effortless",
        "stand out",
        "achieve",
    ],
    "authority": [
        "trusted",
        "expert",
        "proven",
        "certified",
        "experienced",
        "leading",
    ],
    "urgency": [
        "today",
        "now",
        "limited",
        "soon",
        "exclusive",
        "available",
    ],
    "outcome": [
        "growth",
        "save",
        "increase",
        "improve",
        "transform",
        "accelerate",
    ],
}


def calculate_conversion_score(
    profile: dict[str, Any],
) -> None:
    breakdown = {}
    total_score = 0

    for field in CONVERSION_SCORE_FIELDS:
        weight = CONVERSION_SCORE_WEIGHTS.get(
            field,
            0,
        )

        value = profile.get(field)

        score = weight if value else 0

        breakdown[
            field.replace(
                "selected_",
                "",
            ).replace(
                "_type",
                "",
            )
        ] = score

        total_score += score

    profile[
        "conversion_score_breakdown"
    ] = breakdown

    profile[
        "conversion_score"
    ] = total_score


def keyword_score(
    text: str,
    keywords: list[str],
    max_score: int,
) -> int:
    if not text:
        return 0

    text_lower = text.lower()

    matches = sum(
        1
        for keyword in keywords
        if keyword in text_lower
    )

    return min(
        max_score,
        matches,
    )


def length_quality_score(
    text: str,
    max_score: int = 10,
) -> int:
    if not text:
        return 0

    length = len(
        text.split()
    )

    if length < 3:
        return 2

    if length < 5:
        return 5

    if length < 8:
        return 8

    return max_score


def calculate_quality_score(
    profile: dict[str, Any],
) -> None:
    hero_text = str(
        profile.get(
            "selected_hero",
            {},
        ).get(
            "headline",
            "",
        )
    )

    cta_text = str(
        profile.get(
            "cta",
            "",
        )
    )

    offer_text = str(
        profile.get(
            "selected_offer",
            {},
        ).get(
            "headline",
            "",
        )
    )

    trust_text = str(
        profile.get(
            "selected_trust",
            {},
        ).get(
            "headline",
            "",
        )
    )

    authority_text = str(
        profile.get(
            "selected_authority",
            {},
        ).get(
            "headline",
            "",
        )
    )

    urgency_text = str(
        profile.get(
            "selected_urgency",
            {},
        ).get(
            "headline",
            "",
        )
    )

    outcome_text = str(
        profile.get(
            "selected_outcome",
            {},
        ).get(
            "headline",
            "",
        )
    )

    breakdown = {
        "hero": length_quality_score(
            hero_text,
            10,
        ),
        "cta": length_quality_score(
            cta_text,
            10,
        ),
        "offer": length_quality_score(
            offer_text,
            8,
        ),
        "trust": length_quality_score(
            trust_text,
            8,
        ),
        "emotional_impact": keyword_score(
            hero_text,
            QUALITY_KEYWORDS[
                "emotional"
            ],
            8,
        ),
        "clarity": keyword_score(
            hero_text,
            QUALITY_KEYWORDS[
                "clarity"
            ],
            10,
        ),
        "specificity": keyword_score(
            hero_text,
            QUALITY_KEYWORDS[
                "specificity"
            ],
            10,
        ),
        "authority": keyword_score(
            authority_text,
            QUALITY_KEYWORDS[
                "authority"
            ],
            8,
        ),
        "urgency": keyword_score(
            urgency_text,
            QUALITY_KEYWORDS[
                "urgency"
            ],
            6,
        ),
        "outcome": keyword_score(
            outcome_text,
            QUALITY_KEYWORDS[
                "outcome"
            ],
            10,
        ),
    }

    quality_score = sum(
        breakdown.values()
    )

    profile[
        "quality_score_breakdown"
    ] = breakdown

    profile[
        "quality_score"
    ] = quality_score

    conversion_score = int(
        profile.get(
            "conversion_score",
            0,
        )
    )

    overall_score = int(
        (
            conversion_score
            + quality_score
        ) / 2
    )

    profile[
        "overall_score"
    ] = overall_score
