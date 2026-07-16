from __future__ import annotations

from typing import Any


def render_layout(
    *,
    profile: dict[str, Any],
    sections: dict[str, str],
) -> str:
    """
    Render a visual-first layout.

    This initial implementation is intentionally
    pass-through to preserve existing behavior.
    """

    return "\n".join(
        sections.values()
    )
