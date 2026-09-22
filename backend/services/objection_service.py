from typing import Any

from backend.domain.website_state import (
    WebsiteState,
)
from backend.services.objection_selector import (
    _normalize_objection_variants,
    select_objection_variant,
)


def _apply_selected_objection(
    profile: dict[str, Any],
) -> None:

    selected_objection = (
        select_objection_variant(
            objection_variants=profile.get(
                "objection_variants",
                [],
            ),
            conversion_strategy=profile.get(
                "conversion_strategy",
                "general",
            ),
        )
    )

    profile[
        "selected_objection_type"
    ] = selected_objection["type"]

    profile[
        "selected_objection"
    ] = selected_objection


def apply_objection(
    profile: dict[str, Any],
    state: WebsiteState,
) -> None:

    _normalize_objection_variants(
        profile
    )

    _apply_selected_objection(
        profile
    )

    selected_objection = profile.get(
        "selected_objection",
        {},
    )

    if not isinstance(
        selected_objection,
        dict,
    ):
        selected_objection = {}

    selected_objection_type = str(
        profile.get(
            "selected_objection_type",
            "",
        )
        or ""
    )

    state.objection.selected_objection_type = (
        selected_objection_type
    )

    state.objection.selected_objection = (
        selected_objection.copy()
    )
