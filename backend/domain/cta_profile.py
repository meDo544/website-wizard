from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class CTAProfile:
    cta: str = ""
    selected_cta_type: str = ""
    selected_cta: dict[str, Any] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CTAProfile":
        return cls(
            cta=data.get("cta", ""),
            selected_cta_type=data.get("selected_cta_type", ""),
            selected_cta=data.get("selected_cta"),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

