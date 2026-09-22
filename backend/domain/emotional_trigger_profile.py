from dataclasses import dataclass, field
from typing import Any


@dataclass
class EmotionalTriggerProfile:
    selected_emotional_trigger_type: str = "general"
    selected_emotional_trigger: dict[str, Any] = field(
        default_factory=dict
    )

    @classmethod
    def from_dict(
        cls,
        profile: dict[str, Any],
    ) -> "EmotionalTriggerProfile":
        selected_emotional_trigger = profile.get(
            "selected_emotional_trigger",
            {},
        )

        if not isinstance(
            selected_emotional_trigger,
            dict,
        ):
            selected_emotional_trigger = {}

        return cls(
            selected_emotional_trigger_type=str(
                profile.get(
                    "selected_emotional_trigger_type",
                    "general",
                )
                or "general"
            ),
            selected_emotional_trigger=(
                selected_emotional_trigger.copy()
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "selected_emotional_trigger_type": (
                self.selected_emotional_trigger_type
            ),
            "selected_emotional_trigger": (
                self.selected_emotional_trigger.copy()
            ),
        }
