from typing import Any

from backend.domain.website_state import WebsiteState


def _apply_selected_cta(
    profile: dict[str, Any],
    state: WebsiteState,
) -> None:
    ...


def _enforce_cta_priority_rules(
    profile: dict[str, Any],
    state: WebsiteState,
) -> None:
    ...


def apply_cta(
    profile: dict[str, Any],
    state: WebsiteState,
) -> None:
    _apply_selected_cta(
        profile,
        state,
    )

    _enforce_cta_priority_rules(
        profile,
        state,
    )

