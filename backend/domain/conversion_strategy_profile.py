from dataclasses import dataclass, field
from typing import Any


@dataclass
class ConversionStrategyProfile:
    conversion_strategy: str = "general"
    website_identity: dict[str, Any] = field(
        default_factory=dict
    )

    @classmethod
    def from_dict(
        cls,
        profile: dict[str, Any],
    ) -> "ConversionStrategyProfile":

        conversion_strategy = str(
            profile.get(
                "conversion_strategy",
                "general",
            )
        )

        website_identity = profile.get(
            "website_identity",
            {},
        )

        website_identity.get(
            "cta_strategy",
            conversion_strategy,
        )

        return cls(
            conversion_strategy=conversion_strategy,
            website_identity=dict(
                website_identity
            ),
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {
            "conversion_strategy":
                self.conversion_strategy,
            "website_identity":
                dict(self.website_identity),
        }
