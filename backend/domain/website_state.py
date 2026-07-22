from dataclasses import dataclass, field
from typing import Any

from backend.domain.business_profile import BusinessProfile
from backend.domain.hero_profile import HeroProfile
from backend.domain.cta_profile import CTAProfile
from backend.domain.offer_profile import OfferProfile
from backend.domain.trust_profile import TrustProfile

@dataclass
class WebsiteState:
    business: BusinessProfile
    hero: HeroProfile
    cta: CTAProfile
    offer: OfferProfile
    trust: TrustProfile

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
            raw_profile=profile.copy(),
        )

    def to_profile(self) -> dict[str, Any]:
        profile = self.raw_profile.copy()

        profile.update(self.business.to_dict())
        profile.update(self.hero.to_dict())
        profile.update(self.cta.to_dict())
        profile.update(self.offer.to_dict())
        profile.update(self.trust.to_dict())

        return profile
