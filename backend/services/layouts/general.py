from __future__ import annotations

from typing import Any


def render_layout(
    *,
    profile: dict[str, Any],
    content_html: str,
) -> str:
    """
    Render the general fallback layout.

    This initial implementation is intentionally
    pass-through to preserve existing behavior.
    """

    return content_html
