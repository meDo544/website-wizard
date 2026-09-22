from typing import Any

from backend.domain.website_state import WebsiteState
from backend.services.differentiation_selector import (
    _normalize_differentiation_variants,
    select_differentiation_variant,
)


def _apply_selected_differentiation(
    profile: dict[str, Any],
) -> None:
    selected_differentiation = (
        select_differentiation_variant(
            differentiation_variants=profile.get(
                "differentiation_variants",
                [],
            ),
            conversion_strategy=profile.get(
                "conversion_strategy",
                "general",
            ),
        )
    )

    profile[
        "selected_differentiation_type"
    ] = selected_differentiation["type"]

    profile[
        "selected_differentiation"
    ] = selected_differentiation


def apply_differentiation(
    profile: dict[str, Any],
    state: WebsiteState,
) -> None:
    _normalize_differentiation_variants(
        profile
    )

    _apply_selected_differentiation(
        profile
    )

    state.differentiation.selected_differentiation_type = (
        profile.get(
            "selected_differentiation_type",
            "general",
        )
    )

    selected_differentiation = profile.get(
        "selected_differentiation",
        {},
    )

    if not isinstance(
        selected_differentiation,
        dict,
    ):
        selected_differentiation = {}

    state.differentiation.selected_differentiation = (
        selected_differentiation.copy()
    )
