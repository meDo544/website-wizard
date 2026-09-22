from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class UrgencyProfile:
    selected_urgency_type: str = ""
    selected_urgency: dict[str, Any] | None = None

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "UrgencyProfile":
        return cls(
            selected_urgency_type=data.get(
                "selected_urgency_type",
                "",
            ),
            selected_urgency=data.get(
                "selected_urgency",
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
