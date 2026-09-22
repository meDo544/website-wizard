from typing import Any

from backend.domain.website_state import WebsiteState
from backend.services.emotional_trigger_selector import (
    _normalize_emotional_trigger_variants,
    select_emotional_trigger_variant,
)


def _apply_selected_emotional_trigger(
    profile: dict[str, Any],
) -> None:
    selected_emotional_trigger = (
        select_emotional_trigger_variant(
            emotional_trigger_variants=profile.get(
                "emotional_trigger_variants",
                [],
            ),
            conversion_strategy=profile.get(
                "conversion_strategy",
                "general",
            ),
        )
    )

    profile[
        "selected_emotional_trigger_type"
    ] = selected_emotional_trigger["type"]

    profile[
        "selected_emotional_trigger"
    ] = selected_emotional_trigger


def apply_emotional_trigger(
    profile: dict[str, Any],
    state: WebsiteState,
) -> None:
    _normalize_emotional_trigger_variants(
        profile
    )

    _apply_selected_emotional_trigger(
        profile
    )

    state.emotional_trigger.selected_emotional_trigger_type = (
        profile.get(
            "selected_emotional_trigger_type",
            "general",
        )
    )

    selected_emotional_trigger = profile.get(
        "selected_emotional_trigger",
        {},
    )

    if not isinstance(
        selected_emotional_trigger,
        dict,
    ):
        selected_emotional_trigger = {}

    state.emotional_trigger.selected_emotional_trigger = (
        selected_emotional_trigger.copy()
    )
