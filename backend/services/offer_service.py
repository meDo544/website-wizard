from typing import Any

from backend.domain.website_state import WebsiteState


def _apply_selected_offer(
    profile: dict[str, Any],
    state: WebsiteState,
) -> None:
    ...


def _enforce_offer_priority_rules(
    profile: dict[str, Any],
    state: WebsiteState,
) -> None:
    ...


def apply_offer(
    profile: dict[str, Any],
    state: WebsiteState,
) -> None:
    _apply_selected_offer(
        profile,
        state,
    )

    _enforce_offer_priority_rules(
        profile,
        state,
    )

