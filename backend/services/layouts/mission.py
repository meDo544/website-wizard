from __future__ import annotations

from typing import Any

from backend.services.sections import Section

from backend.services.layouts.orchestrator import (
    order_sections,
)

from backend.services.sections import (
    ConversionRole,
    Section,
)

def render_layout(
    *,
    profile: dict[str, Any],
    sections: dict[str, Section],
) -> str:
    """
    Render a mission-focused layout.

    This initial implementation is intentionally
    pass-through to preserve existing behavior.
    """

    preferred_roles = [
        ConversionRole.EDUCATION,
        ConversionRole.TRUST,
        ConversionRole.ACTION,
    ]

    ordered_sections = order_sections(
        sections=sections,
        preferred_roles=preferred_roles,
    )

    return "\n".join(
        section.html
        for section in ordered_sections
    )





