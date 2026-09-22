from typing import Any


PERFORMANCE_TRACKING_FIELDS = {
    "hero_type": "selected_hero_type",
    "cta_type": "selected_cta_type",
    "offer_type": "selected_offer_type",
    "trust_type": "selected_trust_type",
    "social_proof_type": "selected_social_proof_type",
    "risk_reversal_type": "selected_risk_reversal_type",
    "urgency_type": "selected_urgency_type",
    "objection_type": "selected_objection_type",
    "value_prop_type": "selected_value_prop_type",
    "audience_type": "selected_audience_type",
    "differentiation_type": "selected_differentiation_type",
    "emotional_trigger_type": "selected_emotional_trigger_type",
    "buyer_motivation_type": "selected_buyer_motivation_type",
    "pain_point_type": "selected_pain_point_type",
    "outcome_type": "selected_outcome_type",
    "authority_type": "selected_authority_type",
    "industry_conversion_type": "selected_industry_conversion_type",
}


CONVERSION_PREDICTION_CONFIG = {
    "model_version": "v1",
    "max_conversion_rate": 0.15,
    "confidence_floor": 0.50,
    "confidence_ceiling": 0.95,
}


LEARNING_PROFILE_CONFIG = {
    "model_version": "v1",
    "default_sample_size": 1,
}


OPTIMIZATION_ENGINE_CONFIG = {
    "model_version": "v1",
    "minimum_confidence": 0.50,
}


VARIANT_SELECTION_CONFIG = {
    "model_version": "v1",
    "selection_source": "optimization_engine",
}


SELECTION_OVERRIDE_CONFIG = {
    "model_version": "v1",
    "override_enabled": True,
}


VARIANT_APPLICATION_CONFIG = {
    "model_version": "v1",
    "application_source": "selection_override",
    "applied": True,
}


def build_performance_tracking(
    website_data: dict,
) -> dict:
    performance_tracking = {}

    for (
        output_field,
        source_field,
    ) in PERFORMANCE_TRACKING_FIELDS.items():

        selected_value = website_data.get(
            source_field
        )

        if isinstance(
            selected_value,
            dict,
        ):
            performance_tracking[
                output_field
            ] = selected_value.get(
                "type"
            )
        else:
            performance_tracking[
                output_field
            ] = selected_value

    performance_tracking[
        "conversion_score"
    ] = website_data.get(
        "conversion_score",
        0,
    )

    performance_tracking[
        "quality_score"
    ] = website_data.get(
        "quality_score",
        0,
    )

    performance_tracking[
        "overall_score"
    ] = website_data.get(
        "overall_score",
        0,
    )

    return performance_tracking


def build_conversion_prediction(
    profile: dict[str, Any],
) -> dict:

    conversion_score = int(
        profile.get(
            "conversion_score",
            0,
        )
    )

    quality_score = int(
        profile.get(
            "quality_score",
            0,
        )
    )

    overall_score = int(
        profile.get(
            "overall_score",
            0,
        )
    )

    predicted_conversion_rate = round(
        (
            overall_score / 100
        )
        * CONVERSION_PREDICTION_CONFIG[
            "max_conversion_rate"
        ],
        4,
    )

    confidence = (
        conversion_score
        + quality_score
    ) / 200

    confidence = max(
        CONVERSION_PREDICTION_CONFIG[
            "confidence_floor"
        ],
        confidence,
    )

    confidence = min(
        CONVERSION_PREDICTION_CONFIG[
            "confidence_ceiling"
        ],
        confidence,
    )

    return {
        "predicted_conversion_rate":
            predicted_conversion_rate,
        "prediction_confidence":
            round(
                confidence,
                2,
            ),
        "prediction_model_version":
            CONVERSION_PREDICTION_CONFIG[
                "model_version"
            ],
    }


def build_learning_profile(
    profile: dict[str, Any],
) -> dict:

    performance_tracking = profile.get(
        "performance_tracking",
        {},
    )

    return {
        "industry": profile.get(
            "business_type",
            "general",
        ),
        "sample_size":
            LEARNING_PROFILE_CONFIG[
                "default_sample_size"
            ],
        "average_conversion_score":
            int(
                profile.get(
                    "conversion_score",
                    0,
                )
            ),
        "average_quality_score":
            int(
                profile.get(
                    "quality_score",
                    0,
                )
            ),
        "average_overall_score":
            int(
                profile.get(
                    "overall_score",
                    0,
                )
            ),
        "top_hero_type":
            performance_tracking.get(
                "hero_type",
            ),
        "top_cta_type":
            performance_tracking.get(
                "cta_type",
            ),
        "top_offer_type":
            performance_tracking.get(
                "offer_type",
            ),
        "model_version":
            LEARNING_PROFILE_CONFIG[
                "model_version"
            ],
    }


def build_optimization_recommendation(
    profile: dict[str, Any],
) -> dict:

    performance_tracking = profile.get(
        "performance_tracking",
        {},
    )

    conversion_prediction = profile.get(
        "conversion_prediction",
        {},
    )

    confidence = float(
        conversion_prediction.get(
            "prediction_confidence",
            0,
        )
    )

    return {
        "recommended_hero_type":
            performance_tracking.get(
                "hero_type",
            ),
        "recommended_cta_type":
            performance_tracking.get(
                "cta_type",
            ),
        "recommended_offer_type":
            performance_tracking.get(
                "offer_type",
            ),
        "confidence":
            max(
                confidence,
                OPTIMIZATION_ENGINE_CONFIG[
                    "minimum_confidence"
                ],
            ),
        "model_version":
            OPTIMIZATION_ENGINE_CONFIG[
                "model_version"
            ],
    }


def build_variant_selection_strategy(
    profile: dict[str, Any],
) -> dict:

    optimization_recommendation = (
        profile.get(
            "optimization_recommendation",
            {},
        )
    )

    return {
        "hero_type":
            optimization_recommendation.get(
                "recommended_hero_type",
            ),
        "cta_type":
            optimization_recommendation.get(
                "recommended_cta_type",
            ),
        "offer_type":
            optimization_recommendation.get(
                "recommended_offer_type",
            ),
        "selection_source":
            VARIANT_SELECTION_CONFIG[
                "selection_source"
            ],
        "model_version":
            VARIANT_SELECTION_CONFIG[
                "model_version"
            ],
    }


def build_selection_override(
    profile: dict[str, Any],
) -> dict:

    variant_selection_strategy = (
        profile.get(
            "variant_selection_strategy",
            {},
        )
    )

    return {
        "hero_type":
            variant_selection_strategy.get(
                "hero_type",
            ),
        "cta_type":
            variant_selection_strategy.get(
                "cta_type",
            ),
        "offer_type":
            variant_selection_strategy.get(
                "offer_type",
            ),
        "override_enabled":
            SELECTION_OVERRIDE_CONFIG[
                "override_enabled"
            ],
        "model_version":
            SELECTION_OVERRIDE_CONFIG[
                "model_version"
            ],
    }


def build_variant_application(
    profile: dict[str, Any],
) -> dict:

    selection_override = profile.get(
        "selection_override",
        {},
    )

    return {
        "hero_type":
            selection_override.get(
                "hero_type",
            ),
        "cta_type":
            selection_override.get(
                "cta_type",
            ),
        "offer_type":
            selection_override.get(
                "offer_type",
            ),
        "application_source":
            VARIANT_APPLICATION_CONFIG[
                "application_source"
            ],
        "applied":
            VARIANT_APPLICATION_CONFIG[
                "applied"
            ],
        "model_version":
            VARIANT_APPLICATION_CONFIG[
                "model_version"
            ],
    }
