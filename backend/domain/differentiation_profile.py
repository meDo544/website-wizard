from dataclasses import dataclass, field
from typing import Any


@dataclass
class DifferentiationProfile:
    selected_differentiation_type: str = "general"
    selected_differentiation: dict[str, Any] = field(
        default_factory=dict
    )

    @classmethod
    def from_dict(
        cls,
        profile: dict[str, Any],
    ) -> "DifferentiationProfile":
        selected_differentiation = profile.get(
            "selected_differentiation",
            {},
        )

        if not isinstance(
            selected_differentiation,
            dict,
        ):
            selected_differentiation = {}

        return cls(
            selected_differentiation_type=str(
                profile.get(
                    "selected_differentiation_type",
                    "general",
                )
                or "general"
            ),
            selected_differentiation=(
                selected_differentiation.copy()
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "selected_differentiation_type": (
                self.selected_differentiation_type
            ),
            "selected_differentiation": (
                self.selected_differentiation.copy()
            ),
        }
