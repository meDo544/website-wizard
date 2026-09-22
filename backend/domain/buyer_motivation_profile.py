from dataclasses import dataclass, field
from typing import Any


@dataclass
class BuyerMotivationProfile:
    selected_buyer_motivation_type: str = "general"
    selected_buyer_motivation: dict[str, Any] = field(
        default_factory=dict
    )

    @classmethod
    def from_dict(
        cls,
        profile: dict[str, Any],
    ) -> "BuyerMotivationProfile":
        selected_buyer_motivation = profile.get(
            "selected_buyer_motivation",
            {},
        )

        if not isinstance(
            selected_buyer_motivation,
            dict,
        ):
            selected_buyer_motivation = {}

        return cls(
            selected_buyer_motivation_type=str(
                profile.get(
                    "selected_buyer_motivation_type",
                    "general",
                )
                or "general"
            ),
            selected_buyer_motivation=(
                selected_buyer_motivation.copy()
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "selected_buyer_motivation_type": (
                self.selected_buyer_motivation_type
            ),
            "selected_buyer_motivation": (
                self.selected_buyer_motivation.copy()
            ),
        }
