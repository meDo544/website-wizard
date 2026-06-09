import html


THEMES = {
    "modern": {
        "header_bg": "#2563eb",
        "body_bg": "#f8fafc",
        "text_color": "#1f2937",
        "card_bg": "#ffffff",
    },
    "dark": {
        "header_bg": "#111827",
        "body_bg": "#030712",
        "text_color": "#f9fafb",
        "card_bg": "#1f2937",
    },
    "luxury": {
        "header_bg": "#111111",
        "body_bg": "#faf7f2",
        "text_color": "#1f1f1f",
        "card_bg": "#ffffff",
    },
    "startup": {
        "header_bg": "#7c3aed",
        "body_bg": "#f5f3ff",
        "text_color": "#111827",
        "card_bg": "#ffffff",
    },
}


def render_template(
    *,
    title: str,
    tagline: str,
    hero_title: str,
    hero_subtitle: str,
    seo_title: str,
    seo_description: str,
    content_html: str,
    theme: str = "modern",
    branding: dict | None = None,
) -> str:

    branding = branding or {}

    theme_config = THEMES.get(
        theme,
        THEMES["modern"],
    )

    primary_color = branding.get(
        "primary_color",
        theme_config["header_bg"],
    )

    secondary_color = branding.get(
        "secondary_color",
        theme_config["card_bg"],
    )

    font_family = branding.get(
        "font_family",
        "Arial, sans-serif",
    )

    logo_text = branding.get(
        "logo_text",
        title,
    )

    return f"""
<!DOCTYPE html>
<html lang="en">

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
/>

<title>{html.escape(seo_title or title)}</title>

<meta
    name="description"
    content="{html.escape(seo_description)}"
/>

<style>

body {{
    font-family: {font_family};
    margin: 0;
    background: {theme_config["body_bg"]};
    color: {theme_config["text_color"]};
}}

nav {{
    background: {primary_color};
    padding: 15px 30px;
}}

.logo {{
    color: white;
    font-size: 1.5rem;
    font-weight: bold;
    margin-bottom: 12px;
}}

nav ul {{
    list-style: none;
    display: flex;
    gap: 25px;
    margin: 0;
    padding: 0;
}}

nav a {{
    color: white;
    text-decoration: none;
    font-weight: bold;
}}

nav a:hover {{
    text-decoration: underline;
}}

header {{
    background: {primary_color};
    color: white;
    padding: 80px 40px;
    text-align: center;
}}

.hero-title {{
    font-size: 3rem;
    margin-bottom: 20px;
}}

.hero-subtitle {{
    font-size: 1.25rem;
    max-width: 700px;
    margin: auto;
}}

main {{
    max-width: 1100px;
    margin: auto;
    padding: 50px 30px;
}}

.grid {{
    display: grid;
    grid-template-columns: repeat(
        auto-fit,
        minmax(250px, 1fr)
    );
    gap: 20px;
}}

.card {{
    background: {secondary_color};
    padding: 24px;
    border-radius: 12px;
    box-shadow:
        0 4px 12px rgba(0,0,0,.08);
}}

section {{
    margin-top: 60px;
}}

.cta {{
    background: {primary_color};
    color: white;
    padding: 30px;
    border-radius: 12px;
    text-align: center;
}}

</style>

</head>

<body>

<nav>

    <div class="logo">
        {html.escape(logo_text)}
    </div>

    <ul>
        <li><a href="index.html">Home</a></li>
        <li><a href="about.html">About</a></li>
        <li><a href="services.html">Services</a></li>
        <li><a href="contact.html">Contact</a></li>
    </ul>

</nav>

<header>

<h1 class="hero-title">
{html.escape(hero_title)}
</h1>

<p class="hero-subtitle">
{html.escape(hero_subtitle)}
</p>

</header>

<main>

<section>

<h2>{html.escape(title)}</h2>

<p>{html.escape(tagline)}</p>

</section>

{content_html}

</main>

</body>

</html>
"""

