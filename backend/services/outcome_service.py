from typing import Any

from backend.domain.website_state import WebsiteState
from backend.services.outcome_selector import (
    _normalize_outcome_variants,
    select_outcome_variant,
)


def _apply_selected_outcome(
    profile: dict[str, Any],
) -> None:
    selected_outcome = (
        select_outcome_variant(
            outcome_variants=profile.get(
                "outcome_variants",
                [],
            ),
            conversion_strategy=profile.get(
                "conversion_strategy",
                "general",
            ),
        )
    )

    profile[
        "selected_outcome_type"
    ] = selected_outcome["type"]

    profile[
        "selected_outcome"
    ] = selected_outcome


def apply_outcome(
    profile: dict[str, Any],
    state: WebsiteState,
) -> None:
    _normalize_outcome_variants(
        profile
    )

    _apply_selected_outcome(
        profile
    )

    state.outcome.selected_outcome_type = (
        profile.get(
            "selected_outcome_type",
            "general",
        )
    )

    selected_outcome = profile.get(
        "selected_outcome",
        {},
    )

    if not isinstance(
        selected_outcome,
        dict,
    ):
        selected_outcome = {}

    state.outcome.selected_outcome = (
        selected_outcome.copy()
    )
