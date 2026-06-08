# backend/services/multi_page_generator.py

from __future__ import annotations

from backend.services.templates.base import render_template


def _cards(
    items: list,
) -> str:
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


def _testimonial_cards(
    testimonials: list,
) -> str:
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


def _faq_cards(
    faqs: list,
) -> str:
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


def generate_home_page(
    *,
    profile: dict,
    theme: str = "modern",
) -> str:

    services_html = _cards(
        profile.get(
            "services",
            [],
        )
    )

    features_html = _cards(
        profile.get(
            "features",
            [],
        )
    )

    testimonials_html = _testimonial_cards(
        profile.get(
            "testimonials",
            [],
        )
    )

    content_html = f"""
    <section>
        <h2>Services</h2>

        <div class="grid">
            {services_html}
        </div>
    </section>

    <section>
        <h2>Why Choose Us</h2>

        <div class="grid">
            {features_html}
        </div>
    </section>

    <section>
        <h2>What Our Customers Say</h2>

        <div class="grid">
            {testimonials_html}
        </div>
    </section>

    <section class="cta">
        <h2>Get Started</h2>
        <p>{profile.get("cta", "")}</p>
    </section>
    """

    return render_template(
        title=profile.get(
            "business_name",
            "Website",
        ),
        tagline=profile.get(
            "tagline",
            "",
        ),
        hero_title=profile.get(
            "hero_title",
            "",
        ),
        hero_subtitle=profile.get(
            "hero_subtitle",
            "",
        ),
        seo_title=profile.get(
            "seo_title",
            "",
        ),
        seo_description=profile.get(
            "seo_description",
            "",
        ),
        content_html=content_html,
        theme=theme,
    )


def generate_about_page(
    *,
    profile: dict,
    theme: str = "modern",
) -> str:

    features_html = _cards(
        profile.get(
            "features",
            [],
        )
    )

    content_html = f"""
    <section>
        <h2>About Us</h2>
        <p>{profile.get("about", "")}</p>
    </section>

    <section>
        <h2>What Makes Us Different</h2>

        <div class="grid">
            {features_html}
        </div>
    </section>
    """

    return render_template(
        title=profile.get(
            "business_name",
            "About Us",
        ),
        tagline=profile.get(
            "tagline",
            "",
        ),
        hero_title="About Us",
        hero_subtitle=profile.get(
            "about",
            "",
        ),
        seo_title=f"About {profile.get('business_name', 'Us')}",
        seo_description=profile.get(
            "seo_description",
            "",
        ),
        content_html=content_html,
        theme=theme,
    )


def generate_services_page(
    *,
    profile: dict,
    theme: str = "modern",
) -> str:

    services_html = _cards(
        profile.get(
            "services",
            [],
        )
    )

    faqs_html = _faq_cards(
        profile.get(
            "faqs",
            [],
        )
    )

    content_html = f"""
    <section>
        <h2>Our Services</h2>

        <div class="grid">
            {services_html}
        </div>
    </section>

    <section>
        <h2>Frequently Asked Questions</h2>

        <div class="grid">
            {faqs_html}
        </div>
    </section>
    """

    return render_template(
        title=profile.get(
            "business_name",
            "Services",
        ),
        tagline=profile.get(
            "tagline",
            "",
        ),
        hero_title="Our Services",
        hero_subtitle=profile.get(
            "tagline",
            "",
        ),
        seo_title=f"Services | {profile.get('business_name', 'Website')}",
        seo_description=profile.get(
            "seo_description",
            "",
        ),
        content_html=content_html,
        theme=theme,
    )


def generate_contact_page(
    *,
    profile: dict,
    theme: str = "modern",
) -> str:

    contact = profile.get(
        "contact",
        {},
    )

    content_html = f"""
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

    <section class="cta">
        <h2>Ready to Get Started?</h2>
        <p>{profile.get("cta", "")}</p>
    </section>
    """

    return render_template(
        title=profile.get(
            "business_name",
            "Contact",
        ),
        tagline=profile.get(
            "tagline",
            "",
        ),
        hero_title="Contact Us",
        hero_subtitle="We would love to hear from you.",
        seo_title=f"Contact | {profile.get('business_name', 'Website')}",
        seo_description=profile.get(
            "seo_description",
            "",
        ),
        content_html=content_html,
        theme=theme,
    )


def generate_multi_page_site(
    *,
    profile: dict,
    theme: str = "modern",
) -> dict[str, str]:
    """
    Generate a simple multi-page website from one GPT profile.
    """

    return {
        "index.html": generate_home_page(
            profile=profile,
            theme=theme,
        ),
        "about.html": generate_about_page(
            profile=profile,
            theme=theme,
        ),
        "services.html": generate_services_page(
            profile=profile,
            theme=theme,
        ),
        "contact.html": generate_contact_page(
            profile=profile,
            theme=theme,
        ),
    }

