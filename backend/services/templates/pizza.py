from backend.services.templates.base import render_template


def generate(profile: dict) -> str:

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

    content_html = f"""
    <h2>Featured Pizzas</h2>

    <div class="grid">
        {services_html}
    </div>

    <section>
        <h2>About Us</h2>
        <p>{profile.get("about", "")}</p>
    </section>

    <section>
        <h2>Get Started</h2>
        <p>{profile.get("cta", "")}</p>
    </section>
    """

    return render_template(
        title=profile.get(
            "business_name",
            "Pizza Shop",
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
    )

