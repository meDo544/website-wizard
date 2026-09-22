from typing import Any

from backend.domain.product_profile import (
    ProductProfile,
)
from backend.domain.website_state import (
    WebsiteState,
)


def apply_products(
    profile: dict[str, Any],
    state: WebsiteState,
) -> None:

    products = ProductProfile.from_dict(
        profile
    )

    profile.update(
        products.to_dict()
    )

    state.products = products
