from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass
class BusinessProfile:
    website_identity: dict[str, Any]
    branding: dict[str, Any]

    industry: str = "general"
    template_name: str = "modern"
    layout_type: str = "general"
    primary_goal: str = "lead_generation"

    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BusinessProfile":
        return cls(
            website_identity=data.get("website_identity", {}),
            branding=data.get("branding", {}),
            industry=data.get("industry", "general"),
            template_name=data.get("template_name", "modern"),
            layout_type=data.get("layout_type", "general"),
            primary_goal=data.get("primary_goal", "lead_generation"),
            metadata=data.get("metadata", {}),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


