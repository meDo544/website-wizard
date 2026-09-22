from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class SocialProofProfile:
    selected_social_proof_type: str = ""
    selected_social_proof: dict[str, Any] | None = None

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "SocialProofProfile":
        return cls(
            selected_social_proof_type=data.get(
                "selected_social_proof_type",
                "",
            ),
            selected_social_proof=data.get(
                "selected_social_proof",
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
