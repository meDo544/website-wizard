from typing import Any

from backend.domain.website_state import WebsiteState
from backend.services.authority_selector import (
    _normalize_authority_variants,
    select_authority_variant,
)


def _apply_selected_authority(
    profile: dict[str, Any],
) -> None:
    selected_authority = (
        select_authority_variant(
            authority_variants=profile.get(
                "authority_variants",
                [],
            ),
            conversion_strategy=profile.get(
                "conversion_strategy",
                "general",
            ),
        )
    )

    profile[
        "selected_authority_type"
    ] = selected_authority["type"]

    profile[
        "selected_authority"
    ] = selected_authority


def apply_authority(
    profile: dict[str, Any],
    state: WebsiteState,
) -> None:
    _normalize_authority_variants(
        profile
    )

    _apply_selected_authority(
        profile
    )

    state.authority.selected_authority_type = (
        profile.get(
            "selected_authority_type",
            "general",
        )
    )

    selected_authority = profile.get(
        "selected_authority",
        {},
    )

    if not isinstance(
        selected_authority,
        dict,
    ):
        selected_authority = {}

    state.authority.selected_authority = (
        selected_authority.copy()
    )
