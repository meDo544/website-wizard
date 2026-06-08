from backend.services.templates.pizza import (
    generate as pizza_template,
)

from backend.services.templates.restaurant import (
    generate as restaurant_template,
)

from backend.services.templates.electronics import (
    generate as electronics_template,
)


TEMPLATES = {
    "Pizza Shop": pizza_template,
    "Restaurant": restaurant_template,
    "Electronics Shop": electronics_template,
}


def generate_website(
    *,
    profile: dict,
    business_type: str,
    theme: str = "modern",
) -> str:
    """
    Generate a website from a GPT profile.

    Business templates handle content layout.

    Theme controls visual styling.
    """

    template = TEMPLATES.get(
        business_type,
        electronics_template,
    )

    return template(
        profile,
        theme=theme,
    )

