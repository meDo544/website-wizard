from typing import Any

from backend.domain.industry_component_profile import (
    IndustryComponentProfile,
)
from backend.domain.website_state import (
    WebsiteState,
)
from backend.services.industry_component_selector import (
    get_active_components,
    get_industry_components,
)


def apply_industry_components(
    profile: dict[str, Any],
    state: WebsiteState,
) -> None:

    profile["industry_components"] = (
        get_industry_components(
            profile
        )
    )

    profile["active_components"] = (
        get_active_components(
            profile
        )
    )

    state.industry_components = (
        IndustryComponentProfile.from_dict(
            profile
        )
    )
