from dataclasses import dataclass, asdict
from typing import Any

@dataclass
class TrustProfile:
    trust_title: str = ""
    trust_subtitle: str = ""
    selected_trust_type: str = ""
    selected_trust: dict[str, Any] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TrustProfile":
        return cls(
            trust_title=data.get("trust_title", ""),
            trust_subtitle=data.get("trust_subtitle", ""),
            selected_trust_type=data.get("selected_trust_type", ""),
            selected_trust=data.get("selected_trust"),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


