from typing import Any

from backend.domain.website_state import (
    WebsiteState,
)
from backend.services.value_prop_selector import (
    _normalize_value_prop_variants,
    select_value_prop_variant,
)


def _apply_selected_value_prop(
    profile: dict[str, Any],
) -> None:

    selected_value_prop = (
        select_value_prop_variant(
            value_prop_variants=profile.get(
                "value_prop_variants",
                [],
            ),
            conversion_strategy=profile.get(
                "conversion_strategy",
                "general",
            ),
        )
    )

    profile[
        "selected_value_prop_type"
    ] = selected_value_prop["type"]

    profile[
        "selected_value_prop"
    ] = selected_value_prop


def apply_value_prop(
    profile: dict[str, Any],
    state: WebsiteState,
) -> None:

    _normalize_value_prop_variants(
        profile
    )

    _apply_selected_value_prop(
        profile
    )

    state.value_prop.selected_value_prop_type = (
        profile.get(
            "selected_value_prop_type",
            "",
        )
    )

    selected_value_prop = profile.get(
        "selected_value_prop",
        {},
    )

    if not isinstance(
        selected_value_prop,
        dict,
    ):
        selected_value_prop = {}

    state.value_prop.selected_value_prop = (
        selected_value_prop.copy()
    )
