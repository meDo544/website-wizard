from __future__ import annotations

from backend.services.sections import (
    ConversionRole,
    Section,
)

from backend.services.layouts.orchestrator import (
    order_sections,
)

from backend.services.sections import (
    ConversionRole,
    Section,
)

def order_sections(
    *,
    sections: dict[str, Section],
    preferred_roles: list[ConversionRole],
) -> list[Section]:

    ordered: list[Section] = []
    used: set[str] = set()

    for role in preferred_roles:

        for name, section in sections.items():

            if (
                section.visible
                and section.conversion_role == role
            ):
                ordered.append(section)
                used.add(name)

    for name, section in sections.items():

        if (
            name not in used
            and section.visible
        ):
            ordered.append(section)

    return ordered
