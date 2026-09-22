from dataclasses import dataclass, field
from typing import Any


@dataclass
class ObjectionProfile:
    selected_objection_type: str = ""
    selected_objection: dict[str, Any] = field(
        default_factory=dict
    )

    @classmethod
    def from_dict(
        cls,
        profile: dict[str, Any],
    ) -> "ObjectionProfile":
        selected_objection = profile.get(
            "selected_objection",
            {},
        )

        if not isinstance(
            selected_objection,
            dict,
        ):
            selected_objection = {}

        return cls(
            selected_objection_type=str(
                profile.get(
                    "selected_objection_type",
                    "",
                )
                or ""
            ),
            selected_objection=selected_objection.copy(),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "selected_objection_type": (
                self.selected_objection_type
            ),
            "selected_objection": (
                self.selected_objection.copy()
            ),
        }
