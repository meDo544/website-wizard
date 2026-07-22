from dataclasses import dataclass, asdict
from typing import Any

@dataclass
class OfferProfile:
    offer_title: str = ""
    offer_subtitle: str = ""
    selected_offer_type: str = ""
    selected_offer: dict[str, Any] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "OfferProfile":
        return cls(
            offer_title=data.get("offer_title", ""),
            offer_subtitle=data.get("offer_subtitle", ""),
            selected_offer_type=data.get("selected_offer_type", ""),
            selected_offer=data.get("selected_offer"),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

