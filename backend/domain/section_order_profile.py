from dataclasses import dataclass, field
from typing import Any


@dataclass
class SectionOrderProfile:
    section_order: list[str] = field(
        default_factory=list
    )

    @classmethod
    def from_dict(
        cls,
        profile: dict[str, Any],
    ) -> "SectionOrderProfile":
        section_order = profile.get(
            "section_order",
            [],
        )

        if not isinstance(
            section_order,
            list,
        ):
            section_order = []

        return cls(
            section_order=list(
                section_order
            ),
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "section_order": list(
                self.section_order
            ),
        }
