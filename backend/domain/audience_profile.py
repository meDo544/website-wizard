from dataclasses import dataclass, field
from typing import Any


@dataclass
class AudienceProfile:
    selected_audience_type: str = "general"
    selected_audience: dict[str, Any] = field(
        default_factory=dict
    )

    @classmethod
    def from_dict(
        cls,
        profile: dict[str, Any],
    ) -> "AudienceProfile":
        selected_audience = profile.get(
            "selected_audience",
            {},
        )

        if not isinstance(
            selected_audience,
            dict,
        ):
            selected_audience = {}

        selected_audience_type = str(
            profile.get(
                "selected_audience_type",
                selected_audience.get(
                    "type",
                    "general",
                ),
            )
            or "general"
        ).strip()

        return cls(
            selected_audience_type=(
                selected_audience_type
            ),
            selected_audience=(
                selected_audience.copy()
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "selected_audience_type": (
                self.selected_audience_type
            ),
            "selected_audience": (
                self.selected_audience.copy()
            ),
        }
