from typing import Any

from backend.domain.website_state import WebsiteState


def _apply_selected_hero(
    profile: dict[str, Any],
    state: WebsiteState,
) -> None:
    ...


def _enforce_hero_priority_rules(
    profile: dict[str, Any],
    state: WebsiteState,
) -> None:
    ...


def apply_hero(
    profile: dict[str, Any],
    state: WebsiteState,
) -> None:
    _apply_selected_hero(
        profile,
        state,
    )

    enforce_hero_priority_rules(
        profile,
        state,
    )


