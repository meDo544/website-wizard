from dataclasses import dataclass, field
from typing import Any


@dataclass
class OutcomeProfile:
    selected_outcome_type: str = "general"
    selected_outcome: dict[str, Any] = field(
        default_factory=dict
    )

    @classmethod
    def from_dict(
        cls,
        profile: dict[str, Any],
    ) -> "OutcomeProfile":
        selected_outcome = profile.get(
            "selected_outcome",
            {},
        )

        if not isinstance(
            selected_outcome,
            dict,
        ):
            selected_outcome = {}

        return cls(
            selected_outcome_type=str(
                profile.get(
                    "selected_outcome_type",
                    "general",
                )
                or "general"
            ),
            selected_outcome=(
                selected_outcome.copy()
            ),
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "selected_outcome_type": (
                self.selected_outcome_type
            ),
            "selected_outcome": (
                self.selected_outcome.copy()
            ),
        }
