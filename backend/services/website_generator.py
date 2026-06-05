from backend.services.templates.pizza import (
    generate as pizza_template,
)

from backend.services.templates.restaurant import (
    generate as restaurant_template,
)

from backend.services.templates.electronics import (
    generate as electronics_template,
)


# ------------------------------------------------
# TEMPLATE REGISTRY
# ------------------------------------------------

TEMPLATES = {
    "Pizza Shop": pizza_template,
    "Restaurant": restaurant_template,
    "Electronics Shop": electronics_template,
}


# ------------------------------------------------
# WEBSITE GENERATOR
# ------------------------------------------------

def generate_website(
    prompt: str,
    business_type: str,
) -> str:

    template = TEMPLATES.get(
        business_type,
        electronics_template,
    )

    return template(prompt)
