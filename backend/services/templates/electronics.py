from backend.services.templates.base import render_template


def generate(
    profile: dict,
    theme: str = "modern",
) -> str:

    services_html = "".join(
        [
            f"""
            <div class="card">
                <h3>{service}</h3>
            </div>
            """
            for service in profile.get(
                "services",
                [],
            )
        ]
    )

    features_html = "".join(
        [
            f"""
            <div class="card">
                <h3>{feature}</h3>
            </div>
            """
            for feature in profile.get(
                "features",
                [],
            )
        ]
    )

    testimonials_html = "".join(
        [
            f"""
            <div class="card">
                <strong>{item.get("name", "")}</strong>
                <p>{item.get("quote", "")}</p>
            </div>
            """
            for item in profile.get(
                "testimonials",
                [],
            )
        ]
    )

    faqs_html = "".join(
        [
            f"""
            <div class="card">
                <h3>{item.get("question", "")}</h3>
                <p>{item.get("answer", "")}</p>
            </div>
            """
            for item in profile.get(
                "faqs",
                [],
            )
        ]
    )

    contact = profile.get(
        "contact",
        {},
    )

    content_html = f"""
    <section>
        <h2>Featured Products</h2>

        <div class="grid">
            {services_html}
        </div>
    </section>

    <section>
        <h2>About Us</h2>
        <p>{profile.get("about", "")}</p>
    </section>

    <section>
        <h2>Why Shop With Us</h2>

        <div class="grid">
            {features_html}
        </div>
    </section>

    <section>
        <h2>Customer Testimonials</h2>

        <div class="grid">
            {testimonials_html}
        </div>
    </section>

    <section>
        <h2>Frequently Asked Questions</h2>

        <div class="grid">
            {faqs_html}
        </div>
    </section>

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
        <h2>Shop Now</h2>
        <p>{profile.get("cta", "")}</p>
    </section>
    """

    return render_template(
        title=profile.get(
            "business_name",
            "Electronics Store",
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
        branding=profile.get(
            "branding",
            {},
        ),
    )

