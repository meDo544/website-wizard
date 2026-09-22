from typing import Any

from backend.domain.website_state import WebsiteState
from backend.services.industry_conversion_selector import (
    _normalize_industry_conversion_variants,
    select_industry_conversion_variant,
)


def _apply_selected_industry_conversion(
    profile: dict[str, Any],
) -> None:
    selected_industry_conversion = (
        select_industry_conversion_variant(
            industry_conversion_variants=profile.get(
                "industry_conversion_variants",
                [],
            ),
            conversion_strategy=profile.get(
                "conversion_strategy",
                "general",
            ),
        )
    )

    profile[
        "selected_industry_conversion_type"
    ] = selected_industry_conversion["type"]

    profile[
        "selected_industry_conversion"
    ] = selected_industry_conversion


def apply_industry_conversion(
    profile: dict[str, Any],
    state: WebsiteState,
) -> None:
    _normalize_industry_conversion_variants(
        profile
    )

    _apply_selected_industry_conversion(
        profile
    )

    state.industry_conversion.selected_industry_conversion_type = (
        profile.get(
            "selected_industry_conversion_type",
            "general",
        )
    )

    selected_industry_conversion = profile.get(
        "selected_industry_conversion",
        {},
    )

    if not isinstance(
        selected_industry_conversion,
        dict,
    ):
        selected_industry_conversion = {}

    state.industry_conversion.selected_industry_conversion = (
        selected_industry_conversion.copy()
    )
