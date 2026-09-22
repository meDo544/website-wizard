from typing import Any

from backend.domain.website_state import WebsiteState
from backend.services.buyer_motivation_selector import (
    _normalize_buyer_motivation_variants,
    select_buyer_motivation_variant,
)


def _apply_selected_buyer_motivation(
    profile: dict[str, Any],
) -> None:
    selected_buyer_motivation = (
        select_buyer_motivation_variant(
            buyer_motivation_variants=profile.get(
                "buyer_motivation_variants",
                [],
            ),
            conversion_strategy=profile.get(
                "conversion_strategy",
                "general",
            ),
        )
    )

    profile[
        "selected_buyer_motivation_type"
    ] = selected_buyer_motivation["type"]

    profile[
        "selected_buyer_motivation"
    ] = selected_buyer_motivation


def apply_buyer_motivation(
    profile: dict[str, Any],
    state: WebsiteState,
) -> None:
    _normalize_buyer_motivation_variants(
        profile
    )

    _apply_selected_buyer_motivation(
        profile
    )

    state.buyer_motivation.selected_buyer_motivation_type = (
        profile.get(
            "selected_buyer_motivation_type",
            "general",
        )
    )

    selected_buyer_motivation = profile.get(
        "selected_buyer_motivation",
        {},
    )

    if not isinstance(
        selected_buyer_motivation,
        dict,
    ):
        selected_buyer_motivation = {}

    state.buyer_motivation.selected_buyer_motivation = (
        selected_buyer_motivation.copy()
    )
