from __future__ import annotations

from typing import Any

from backend.services.sections import Section

def render_layout(
    *,
    profile: dict[str, Any],
    sections: dict[str, Section],
) -> str:
    """
    Render a visual-first layout.

    This initial implementation is intentionally
    pass-through to preserve existing behavior.
    """

    return "\n".join(
        section.html
        for section in sections.values()
        if section.visible
    )


