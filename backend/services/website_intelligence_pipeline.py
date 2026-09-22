import uuid
from typing import Any

from backend.domain.website_state import WebsiteState

from backend.services.business_classifier import (
    classify_business_profile,
)
from backend.services.business_profile_validator import (
    validate_business_profile,
)
from backend.services.section_order_service import (
    apply_section_order,
)
from backend.services.conversion_strategy_service import (
    apply_conversion_strategy,
)
from backend.services.risk_reversal_service import (
    apply_risk_reversal,
)
from backend.services.product_service import (
    apply_products,
)
from backend.services.hero_service import (
    apply_hero,
)
from backend.services.cta_service import (
    apply_cta,
)
from backend.services.offer_service import (
    apply_offer,
)
from backend.services.trust_service import (
    apply_trust,
)
from backend.services.social_proof_service import (
    apply_social_proof,
)
from backend.services.urgency_service import (
    apply_urgency,
)
from backend.services.objection_service import (
    apply_objection,
)
from backend.services.value_prop_service import (
    apply_value_prop,
)
from backend.services.audience_service import (
    apply_audience,
)
from backend.services.differentiation_service import (
    apply_differentiation,
)
from backend.services.emotional_trigger_service import (
    apply_emotional_trigger,
)
from backend.services.buyer_motivation_service import (
    apply_buyer_motivation,
)
from backend.services.pain_point_service import (
    apply_pain_point,
)
from backend.services.outcome_service import (
    apply_outcome,
)
from backend.services.authority_service import (
    apply_authority,
)
from backend.services.industry_conversion_service import (
    apply_industry_conversion,
)
from backend.services.industry_component_service import (
    apply_industry_components,
)
from backend.services.scoring_calculator import (
    calculate_conversion_score,
    calculate_quality_score,
)
from backend.services.optimization_pipeline import (
    build_performance_tracking,
    build_conversion_prediction,
    build_learning_profile,
    build_optimization_recommendation,
    build_variant_selection_strategy,
    build_selection_override,
    build_variant_application,
)
from backend.services.learning_pipeline import (
    build_feedback_collection,
    build_feedback_outcome,
    build_learning_signal,
    build_learning_accumulator,
    build_adaptive_memory,
    build_memory_consolidation,
    build_optimization_knowledge,
    build_knowledge_refinement,
    build_optimization_intelligence,
)
from backend.services.autonomous_pipeline import (
    build_autonomous_decision,
    build_autonomous_action,
    build_autonomous_execution,
    build_autonomous_outcome,
    build_autonomous_evaluation,
    build_autonomous_adaptation,
    build_autonomous_evolution,
    build_autonomous_strategy,
    build_autonomous_planning,
    build_autonomous_coordination,
    build_autonomous_orchestration,
    build_autonomous_governance,
    build_autonomous_self_improvement,
    build_recursive_learning,
    build_autonomous_core,
)


def build_ab_test_metadata() -> dict:
    return {
        "test_id": str(uuid.uuid4()),
        "variant_id": "A",
        "variant_group": "default",
        "traffic_allocation": 50,
        "status": "active",
    }


def run_website_intelligence_pipeline(
    profile: dict[str, Any],
) -> dict[str, Any]:

    print(
        "DEBUG business_type:",
        profile.get(
            "website_identity",
            {},
        ).get(
            "business_type",
        ),
    )

    profile = classify_business_profile(
        profile
    )

    print(
        "DEBUG industry:",
        profile.get(
            "industry",
        ),
    )

    validate_business_profile(
        profile
    )

    state = WebsiteState.from_profile(
        profile
    )

    profile = state.to_profile()

    apply_section_order(
        profile,
        state,
    )

    profile = state.to_profile()

    apply_conversion_strategy(
        profile,
        state,
    )

    apply_risk_reversal(
        profile,
        state,
    )

    profile = state.to_profile()

    apply_products(
        profile,
        state,
    )

    apply_hero(
        profile,
        state,
    )

    profile = state.to_profile()

    apply_cta(
        profile,
        state,
    )

    profile = state.to_profile()

    apply_offer(
        profile,
        state,
    )

    profile = state.to_profile()

    apply_trust(
        profile,
        state,
    )

    profile = state.to_profile()

    apply_social_proof(
        profile,
        state,
    )

    profile = state.to_profile()

    apply_urgency(
        profile,
        state,
    )

    profile = state.to_profile()

    apply_objection(
        profile,
        state,
    )

    profile = state.to_profile()

    apply_value_prop(
        profile,
        state,
    )

    profile = state.to_profile()

    apply_audience(
        profile,
        state,
    )

    profile = state.to_profile()

    apply_differentiation(
        profile,
        state,
    )

    profile = state.to_profile()

    apply_emotional_trigger(
        profile,
        state,
    )

    profile = state.to_profile()

    apply_buyer_motivation(
        profile,
        state,
    )

    profile = state.to_profile()

    apply_pain_point(
        profile,
        state,
    )

    profile = state.to_profile()

    apply_outcome(
        profile,
        state,
    )

    profile = state.to_profile()

    apply_authority(
        profile,
        state,
    )

    profile = state.to_profile()

    apply_industry_conversion(
        profile,
        state,
    )

    profile = state.to_profile()

    calculate_conversion_score(
        profile
    )

    print("=" * 60)
    print(
        "selected_offer      =",
        profile.get(
            "selected_offer",
        ),
    )
    print(
        "selected_offer_type =",
        profile.get(
            "selected_offer_type",
        ),
    )
    print(
        "offer_title         =",
        profile.get(
            "offer_title",
        ),
    )
    print(
        "state.offer         =",
        state.offer,
    )
    print("=" * 60)

    calculate_quality_score(
        profile
    )

    profile[
        "performance_tracking"
    ] = build_performance_tracking(
        profile
    )

    profile[
        "ab_testing"
    ] = build_ab_test_metadata()

    profile[
        "conversion_prediction"
    ] = build_conversion_prediction(
        profile
    )

    profile[
        "learning_profile"
    ] = build_learning_profile(
        profile
    )

    profile[
        "optimization_recommendation"
    ] = build_optimization_recommendation(
        profile
    )

    profile[
        "variant_selection_strategy"
    ] = build_variant_selection_strategy(
        profile
    )

    profile[
        "selection_override"
    ] = build_selection_override(
        profile
    )

    profile[
        "variant_application"
    ] = build_variant_application(
        profile
    )

    profile[
        "feedback_collection"
    ] = build_feedback_collection(
        profile
    )

    profile[
        "feedback_outcome"
    ] = build_feedback_outcome(
        profile
    )

    profile[
        "learning_signal"
    ] = build_learning_signal(
        profile
    )

    profile[
        "learning_accumulator"
    ] = build_learning_accumulator(
        profile
    )

    profile[
        "adaptive_memory"
    ] = build_adaptive_memory(
        profile
    )

    profile[
        "memory_consolidation"
    ] = build_memory_consolidation(
        profile
    )

    profile[
        "optimization_knowledge"
    ] = build_optimization_knowledge(
        profile
    )

    profile[
        "knowledge_refinement"
    ] = build_knowledge_refinement(
        profile
    )

    profile[
        "optimization_intelligence"
    ] = build_optimization_intelligence(
        profile
    )

    profile[
        "autonomous_decision"
    ] = build_autonomous_decision(
        profile
    )

    profile[
        "autonomous_action"
    ] = build_autonomous_action(
        profile
    )

    profile[
        "autonomous_execution"
    ] = build_autonomous_execution(
        profile
    )

    profile[
        "autonomous_outcome"
    ] = build_autonomous_outcome(
        profile
    )

    profile[
        "autonomous_evaluation"
    ] = build_autonomous_evaluation(
        profile
    )

    profile[
        "autonomous_adaptation"
    ] = build_autonomous_adaptation(
        profile
    )

    profile[
        "autonomous_evolution"
    ] = build_autonomous_evolution(
        profile
    )

    profile[
        "autonomous_strategy"
    ] = build_autonomous_strategy(
        profile
    )

    profile[
        "autonomous_planning"
    ] = build_autonomous_planning(
        profile
    )

    profile[
        "autonomous_coordination"
    ] = build_autonomous_coordination(
        profile
    )

    profile[
        "autonomous_orchestration"
    ] = build_autonomous_orchestration(
        profile
    )

    profile[
        "autonomous_governance"
    ] = build_autonomous_governance(
        profile
    )

    profile[
        "autonomous_self_improvement"
    ] = build_autonomous_self_improvement(
        profile
    )

    profile[
        "recursive_learning"
    ] = build_recursive_learning(
        profile
    )

    profile[
        "autonomous_core"
    ] = build_autonomous_core(
        profile
    )

    apply_industry_components(
        profile,
        state,
    )

    return profile
