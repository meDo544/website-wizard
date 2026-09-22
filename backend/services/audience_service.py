from typing import Any

from backend.domain.website_state import WebsiteState
from backend.services.audience_selector import (
    _normalize_audience_variants,
    select_audience_variant,
)


def _apply_selected_audience(
    profile: dict[str, Any],
) -> None:

    selected_audience = (
        select_audience_variant(
            audience_variants=profile.get(
                "audience_variants",
                [],
            ),
            conversion_strategy=profile.get(
                "conversion_strategy",
                "general",
            ),
        )
    )

    profile[
        "selected_audience_type"
    ] = selected_audience["type"]

    profile[
        "selected_audience"
    ] = selected_audience


def apply_audience(
    profile: dict[str, Any],
    state: WebsiteState,
) -> None:

    _normalize_audience_variants(
        profile
    )

    _apply_selected_audience(
        profile
    )

    state.audience.selected_audience_type = (
        profile.get(
            "selected_audience_type",
            "general",
        )
    )

    selected_audience = profile.get(
        "selected_audience",
        {},
    )

    if not isinstance(
        selected_audience,
        dict,
    ):
        selected_audience = {}

    state.audience.selected_audience = (
        selected_audience.copy()
    )
