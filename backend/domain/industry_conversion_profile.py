from dataclasses import dataclass, field
from typing import Any


@dataclass
class IndustryConversionProfile:
    selected_industry_conversion_type: str = "general"
    selected_industry_conversion: dict[str, Any] = field(
        default_factory=dict
    )

    @classmethod
    def from_dict(
        cls,
        profile: dict[str, Any],
    ) -> "IndustryConversionProfile":
        selected_industry_conversion = profile.get(
            "selected_industry_conversion",
            {},
        )

        if not isinstance(
            selected_industry_conversion,
            dict,
        ):
            selected_industry_conversion = {}

        return cls(
            selected_industry_conversion_type=str(
                profile.get(
                    "selected_industry_conversion_type",
                    "general",
                )
                or "general"
            ),
            selected_industry_conversion=(
                selected_industry_conversion.copy()
            ),
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "selected_industry_conversion_type": (
                self.selected_industry_conversion_type
            ),
            "selected_industry_conversion": (
                self.selected_industry_conversion.copy()
            ),
        }
