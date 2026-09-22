from dataclasses import dataclass, field
from typing import Any


@dataclass
class PainPointProfile:
    selected_pain_point_type: str = "general"
    selected_pain_point: dict[str, Any] = field(
        default_factory=dict
    )

    @classmethod
    def from_dict(
        cls,
        profile: dict[str, Any],
    ) -> "PainPointProfile":
        selected_pain_point = profile.get(
            "selected_pain_point",
            {},
        )

        if not isinstance(
            selected_pain_point,
            dict,
        ):
            selected_pain_point = {}

        return cls(
            selected_pain_point_type=str(
                profile.get(
                    "selected_pain_point_type",
                    "general",
                )
                or "general"
            ),
            selected_pain_point=(
                selected_pain_point.copy()
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "selected_pain_point_type": (
                self.selected_pain_point_type
            ),
            "selected_pain_point": (
                self.selected_pain_point.copy()
            ),
        }
