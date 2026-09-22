from dataclasses import dataclass, field
from typing import Any

from backend.domain.business_profile import BusinessProfile
from backend.domain.hero_profile import HeroProfile
from backend.domain.cta_profile import CTAProfile
from backend.domain.offer_profile import OfferProfile
from backend.domain.trust_profile import TrustProfile
from backend.domain.social_proof_profile import (
    SocialProofProfile,
)
from backend.domain.risk_reversal_profile import (
    RiskReversalProfile,
)
from backend.domain.urgency_profile import (
    UrgencyProfile,
)
from backend.domain.objection_profile import (
    ObjectionProfile,
)
from backend.domain.value_prop_profile import (
    ValuePropProfile,
)
from backend.domain.audience_profile import (
    AudienceProfile,
)
from backend.domain.differentiation_profile import (
    DifferentiationProfile,
)
from backend.domain.emotional_trigger_profile import (
    EmotionalTriggerProfile,
)
from backend.domain.buyer_motivation_profile import (
    BuyerMotivationProfile,
)
from backend.domain.pain_point_profile import (
    PainPointProfile,
)
from backend.domain.outcome_profile import (
    OutcomeProfile,
)
from backend.domain.authority_profile import (
    AuthorityProfile,
)
from backend.domain.industry_conversion_profile import (
    IndustryConversionProfile,
)
from backend.domain.section_order_profile import (
    SectionOrderProfile,
)
from backend.domain.conversion_strategy_profile import (
    ConversionStrategyProfile,
)
from backend.domain.product_profile import (
    ProductProfile,
)
from backend.domain.industry_component_profile import (
    IndustryComponentProfile,
)


@dataclass
class WebsiteState:
    business: BusinessProfile
    hero: HeroProfile
    cta: CTAProfile
    offer: OfferProfile
    trust: TrustProfile
    social_proof: SocialProofProfile
    risk_reversal: RiskReversalProfile
    urgency: UrgencyProfile
    objection: ObjectionProfile
    value_prop: ValuePropProfile
    audience: AudienceProfile
    differentiation: DifferentiationProfile
    emotional_trigger: EmotionalTriggerProfile
    buyer_motivation: BuyerMotivationProfile
    pain_point: PainPointProfile
    outcome: OutcomeProfile
    authority: AuthorityProfile
    industry_conversion: IndustryConversionProfile
    section_order: SectionOrderProfile
    conversion_strategy: ConversionStrategyProfile
    products: ProductProfile
    industry_components: IndustryComponentProfile

    raw_profile: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_profile(
        cls,
        profile: dict[str, Any],
    ) -> "WebsiteState":
        return cls(
            business=BusinessProfile.from_dict(profile),
            hero=HeroProfile.from_dict(profile),
            cta=CTAProfile.from_dict(profile),
            offer=OfferProfile.from_dict(profile),
            trust=TrustProfile.from_dict(profile),
            social_proof=SocialProofProfile.from_dict(
                profile
            ),
            raw_profile=profile.copy(),
            risk_reversal=RiskReversalProfile.from_dict(
                profile
            ),
            urgency=UrgencyProfile.from_dict(
                profile
            ),
            objection=ObjectionProfile.from_dict(
                profile
            ),
            value_prop=ValuePropProfile.from_dict(
                profile
            ),
            audience=AudienceProfile.from_dict(
                profile
            ),
            differentiation=DifferentiationProfile.from_dict(
                profile
            ),
            emotional_trigger=EmotionalTriggerProfile.from_dict(
                profile
            ),
            buyer_motivation=BuyerMotivationProfile.from_dict(
                profile
            ),
            pain_point=PainPointProfile.from_dict(
                profile
            ),
            outcome=OutcomeProfile.from_dict(
                profile
            ),
            authority=AuthorityProfile.from_dict(
                profile
            ),
            industry_conversion=IndustryConversionProfile.from_dict(
                profile
            ),
            section_order=SectionOrderProfile.from_dict(
                profile
            ),
            conversion_strategy=ConversionStrategyProfile.from_dict(
                profile
            ),
            products=ProductProfile.from_dict(
                profile
            ),
            industry_components=IndustryComponentProfile.from_dict(
                profile
            ),
        )

    def to_profile(self) -> dict[str, Any]:
        profile = self.raw_profile.copy()

        profile.update(self.business.to_dict())
        profile.update(self.hero.to_dict())
        profile.update(self.cta.to_dict())
        profile.update(self.offer.to_dict())
        profile.update(self.trust.to_dict())
        profile.update(
            self.social_proof.to_dict()
        )
        profile.update(
            self.risk_reversal.to_dict()
        )
        profile.update(
            self.urgency.to_dict()
        )
        profile.update(
            self.objection.to_dict()
        )
        profile.update(
            self.value_prop.to_dict()
        )
        profile.update(
            self.audience.to_dict()
        )
        profile.update(
            self.differentiation.to_dict()
        )
        profile.update(
            self.emotional_trigger.to_dict()
        )
        profile.update(
            self.buyer_motivation.to_dict()
        )
        profile.update(
            self.pain_point.to_dict()
        )
        profile.update(
            self.outcome.to_dict()
        )
        profile.update(
            self.authority.to_dict()
        )
        profile.update(
            self.industry_conversion.to_dict()
        )
        profile.update(
            self.section_order.to_dict()
        )
        profile.update(
            self.conversion_strategy.to_dict()
        )
        profile.update(
            self.products.to_dict()
        )
        profile.update(
            self.industry_components.to_dict()
        )

        return profile
