from dataclasses import dataclass, field
from typing import Any


@dataclass
class IndustryComponentProfile:
    industry_components: list[str] = field(
        default_factory=list
    )
    active_components: dict[str, Any] = field(
        default_factory=dict
    )

    @classmethod
    def from_dict(
        cls,
        profile: dict[str, Any],
    ) -> "IndustryComponentProfile":

        industry_components = profile.get(
            "industry_components",
            [],
        )

        active_components = profile.get(
            "active_components",
            {},
        )

        if not isinstance(
            industry_components,
            list,
        ):
            industry_components = []

        if not isinstance(
            active_components,
            dict,
        ):
            active_components = {}

        return cls(
            industry_components=list(
                industry_components
            ),
            active_components=dict(
                active_components
            ),
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {
            "industry_components": list(
                self.industry_components
            ),
            "active_components": dict(
                self.active_components
            ),
        }
