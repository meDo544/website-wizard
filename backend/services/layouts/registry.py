from __future__ import annotations

from collections.abc import Callable
from typing import Any

from backend.services.layouts.authority import (
    render_layout as render_authority_layout,
)

from backend.services.layouts.catalog import (
    render_layout as render_catalog_layout,
)

from backend.services.layouts.product import (
    render_layout as render_product_layout,
)

from backend.services.layouts.visual import (
    render_layout as render_visual_layout,
)

from backend.services.layouts.trust import (
    render_layout as render_trust_layout,
)

from backend.services.layouts.mission import (
    render_layout as render_mission_layout,
)

from backend.services.layouts.general import (
    render_layout as render_general_layout,
)

from backend.services.sections import Section

LayoutRenderer = Callable[..., str]


LAYOUT_REGISTRY: dict[str, LayoutRenderer] = {
    "authority": render_authority_layout,
    "catalog": render_catalog_layout,
    "product": render_product_layout,
    "visual": render_visual_layout,
    "trust": render_trust_layout,
    "mission": render_mission_layout,
    "general": render_general_layout,
}


def normalize_layout_type(
    layout_type: str | None,
) -> str:

    if not layout_type:
        return "general"

    normalized = (
        str(layout_type)
        .strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )

    if normalized not in LAYOUT_REGISTRY:
        return "general"

    return normalized


def get_layout_renderer(
    layout_type: str | None,
) -> LayoutRenderer:

    normalized = normalize_layout_type(
        layout_type
    )

    return LAYOUT_REGISTRY[normalized]


def render_selected_layout(
    *,
    layout_type: str | None,
    profile: dict[str, Any],
    sections: dict[str, Section],
) -> str:

    renderer = get_layout_renderer(
        layout_type
    )

    return renderer(
        profile=profile,
        sections=sections,
    )


