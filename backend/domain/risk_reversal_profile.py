from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class RiskReversalProfile:
    selected_risk_reversal_type: str = ""
    selected_risk_reversal: dict[str, Any] | None = None

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "RiskReversalProfile":
        return cls(
            selected_risk_reversal_type=data.get(
                "selected_risk_reversal_type",
                "",
            ),
            selected_risk_reversal=data.get(
                "selected_risk_reversal",
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
