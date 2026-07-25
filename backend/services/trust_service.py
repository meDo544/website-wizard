from typing import Any

from backend.domain.website_state import WebsiteState


def _apply_selected_trust(
    profile: dict[str, Any],
    state: WebsiteState,
) -> None:
    ...


def _enforce_trust_priority_rules(
    profile: dict[str, Any],
    state: WebsiteState,
) -> None:
    ...


def apply_trust(
    profile: dict[str, Any],
    state: WebsiteState,
) -> None:
    _apply_selected_trust(
        profile,
        state,
    )

    _enforce_trust_priority_rules(
        profile,
        state,
    )

