from dataclasses import dataclass, field
from typing import Any


@dataclass
class ValuePropProfile:
    selected_value_prop_type: str = ""
    selected_value_prop: dict[str, Any] = field(
        default_factory=dict
    )

    @classmethod
    def from_dict(
        cls,
        profile: dict[str, Any],
    ) -> "ValuePropProfile":
        selected_value_prop = profile.get(
            "selected_value_prop",
            {},
        )

        if not isinstance(
            selected_value_prop,
            dict,
        ):
            selected_value_prop = {}

        return cls(
            selected_value_prop_type=str(
                profile.get(
                    "selected_value_prop_type",
                    "",
                )
                or ""
            ),
            selected_value_prop=selected_value_prop.copy(),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "selected_value_prop_type": (
                self.selected_value_prop_type
            ),
            "selected_value_prop": (
                self.selected_value_prop.copy()
            ),
        }
