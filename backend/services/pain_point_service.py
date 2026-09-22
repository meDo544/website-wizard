from typing import Any

from backend.domain.website_state import WebsiteState
from backend.services.pain_point_selector import (
    _normalize_pain_point_variants,
    select_pain_point_variant,
)


def _apply_selected_pain_point(
    profile: dict[str, Any],
) -> None:
    selected_pain_point = (
        select_pain_point_variant(
            pain_point_variants=profile.get(
                "pain_point_variants",
                [],
            ),
            conversion_strategy=profile.get(
                "conversion_strategy",
                "general",
            ),
        )
    )

    profile[
        "selected_pain_point_type"
    ] = selected_pain_point["type"]

    profile[
        "selected_pain_point"
    ] = selected_pain_point


def apply_pain_point(
    profile: dict[str, Any],
    state: WebsiteState,
) -> None:
    _normalize_pain_point_variants(
        profile
    )

    _apply_selected_pain_point(
        profile
    )

    state.pain_point.selected_pain_point_type = (
        profile.get(
            "selected_pain_point_type",
            "general",
        )
    )

    selected_pain_point = profile.get(
        "selected_pain_point",
        {},
    )

    if not isinstance(
        selected_pain_point,
        dict,
    ):
        selected_pain_point = {}

    state.pain_point.selected_pain_point = (
        selected_pain_point.copy()
    )
