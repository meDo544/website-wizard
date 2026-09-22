from dataclasses import dataclass, field
from typing import Any


@dataclass
class AuthorityProfile:
    selected_authority_type: str = "general"
    selected_authority: dict[str, Any] = field(
        default_factory=dict
    )

    @classmethod
    def from_dict(
        cls,
        profile: dict[str, Any],
    ) -> "AuthorityProfile":
        selected_authority = profile.get(
            "selected_authority",
            {},
        )

        if not isinstance(
            selected_authority,
            dict,
        ):
            selected_authority = {}

        return cls(
            selected_authority_type=str(
                profile.get(
                    "selected_authority_type",
                    "general",
                )
                or "general"
            ),
            selected_authority=(
                selected_authority.copy()
            ),
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "selected_authority_type": (
                self.selected_authority_type
            ),
            "selected_authority": (
                self.selected_authority.copy()
            ),
        }
