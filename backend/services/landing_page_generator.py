# backend/services/landing_page_generator.py

from __future__ import annotations

from typing import Any

from backend.services.layouts.registry import (
    render_selected_layout,
)

DEFAULT_SECTION_ORDER = [
    "services",
    "features",
    "products",
    "shipping",
    "payments",
    "returns",
    "testimonials",
    "faqs",
    "contact",
    "cta",
]


def get_section_order(
    profile: dict[str, Any],
) -> list[str]:
    """
    Resolve section order from the GPT profile.

    Falls back to a default conversion-focused order.
    """

    section_order = profile.get(
        "section_order",
        DEFAULT_SECTION_ORDER,
    )

    if not isinstance(section_order, list):
        return DEFAULT_SECTION_ORDER

    return [
        section
        for section in section_order
        if section in DEFAULT_SECTION_ORDER
    ] or DEFAULT_SECTION_ORDER


def render_cards(
    items: list[Any],
) -> str:
    """
    Render a list of strings as cards.
    """

    return "".join(
        [
            f"""
            <div class="card">
                <h3>{item}</h3>
            </div>
            """
            for item in items
        ]
    )


def render_testimonials(
    testimonials: list[dict[str, Any]],
) -> str:
    """
    Render testimonial cards.
    """

    return "".join(
        [
            f"""
            <div class="card">
                <strong>{item.get("name", "")}</strong>
                <p>{item.get("quote", "")}</p>
            </div>
            """
            for item in testimonials
        ]
    )


def render_faqs(
    faqs: list[dict[str, Any]],
) -> str:
    """
    Render FAQ cards.
    """

    return "".join(
        [
            f"""
            <div class="card">
                <h3>{item.get("question", "")}</h3>
                <p>{item.get("answer", "")}</p>
            </div>
            """
            for item in faqs
        ]
    )


def render_services_section(
    profile: dict[str, Any],
) -> str:

    return f"""
    <section>
        <h2>Services</h2>

        <div class="grid">
            {render_cards(profile.get("services", []))}
        </div>
    </section>
    """


def render_features_section(
    profile: dict[str, Any],
) -> str:

    return f"""
    <section>
        <h2>Why Choose Us</h2>

        <div class="grid">
            {render_cards(profile.get("features", []))}
        </div>
    </section>
    """


def render_products_section(
    profile: dict[str, Any],
) -> str:

    products = profile.get(
        "products",
        [],
    )

    if not products:
        return ""

    cards = ""

    for product in products:

        cards += f"""
        <div class="card">
            <h3>{product.get("name", "")}</h3>
            <p>{product.get("description", "")}</p>
        </div>
        """

    return f"""
    <section>
        <h2>Featured Products</h2>

        <div class="grid">
            {cards}
        </div>
    </section>
    """

def render_shipping_section(
    profile: dict[str, Any],
) -> str:

    from backend.services.gpt_website_generator import (
        component_is_active,
    )

    if not component_is_active(
        profile,
        "shipping",
    ):
        return ""

    shipping = profile.get(
        "shipping",
        {},
    )

    if not shipping:
        return ""

    return f"""
    <section>
        <h2>{shipping.get("headline", "Shipping")}</h2>

        <p>
            {shipping.get("description", "")}
        </p>
    </section>
    """

def render_payments_section(
    profile: dict[str, Any],
) -> str:

    from backend.services.gpt_website_generator import (
        component_is_active,
    )

    if not component_is_active(
        profile,
        "payments",
    ):
        return ""

    payments = profile.get(
        "payments",
        {},
    )

    if not payments:
        return ""

    return f"""
    <section>
        <h2>{payments.get("headline", "Payments")}</h2>

        <p>
            {payments.get("description", "")}
        </p>
    </section>
    """

def render_returns_section(
    profile: dict[str, Any],
) -> str:

    from backend.services.gpt_website_generator import (
        component_is_active,
    )

    if not component_is_active(
        profile,
        "returns",
    ):
        return ""

    returns = profile.get(
        "returns",
        {},
    )

    if not returns:
        return ""

    return f"""
    <section>
        <h2>{returns.get("headline", "Returns")}</h2>

        <p>
            {returns.get("description", "")}
        </p>
    </section>
    """

def render_testimonials_section(
    profile: dict[str, Any],
) -> str:

    return f"""
    <section>
        <h2>What Our Customers Say</h2>

        <div class="grid">
            {render_testimonials(profile.get("testimonials", []))}
        </div>
    </section>
    """


def render_faqs_section(
    profile: dict[str, Any],
) -> str:

    return f"""
    <section>
        <h2>Frequently Asked Questions</h2>

        <div class="grid">
            {render_faqs(profile.get("faqs", []))}
        </div>
    </section>
    """


def render_contact_section(
    profile: dict[str, Any],
) -> str:

    contact = profile.get(
        "contact",
        {},
    )

    return f"""
    <section>
        <h2>Contact Us</h2>

        <p>
            <strong>Phone:</strong>
            {contact.get("phone", "")}
        </p>

        <p>
            <strong>Email:</strong>
            {contact.get("email", "")}
        </p>

        <p>
            <strong>Address:</strong>
            {contact.get("address", "")}
        </p>
    </section>
    """


def render_cta_section(
    profile: dict[str, Any],
) -> str:

    return f"""
    <section class="cta">
        <h2>Ready to Get Started?</h2>
        <p>{profile.get("cta", "")}</p>
    </section>
    """


SECTION_RENDERERS = {
    "services": render_services_section,
    "features": render_features_section,
    "products": render_products_section,
    "shipping": render_shipping_section,
    "payments": render_payments_section,
    "returns" : render_returns_section,
    "testimonials": render_testimonials_section,
    "faqs": render_faqs_section,
    "contact": render_contact_section,
    "cta": render_cta_section,
}


def generate_landing_page_content(
    *,
    profile: dict[str, Any],
) -> str:
    """
    Generate ordered landing-page section HTML from a GPT profile.
    """

    sections: list[str] = []

    for section_name in get_section_order(
        profile
    ):

        renderer = SECTION_RENDERERS.get(
            section_name
        )

        if not renderer:
            continue

        sections.append(
            renderer(profile)
        )

    content_html = "\n".join(
        sections
    )

    return render_selected_layout(
        layout_type=profile.get(
            "layout_type",
            "general",
        ),
        profile=profile,
        content_html=content_html,
    )



