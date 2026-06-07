import html


def render_template(
    *,
    title: str,
    tagline: str,
    hero_title: str,
    hero_subtitle: str,
    seo_title: str,
    seo_description: str,
    content_html: str,
) -> str:

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
    font-family: Arial, sans-serif;
    margin: 0;
    background: #f8fafc;
    color: #1f2937;
}}

header {{
    background: #2563eb;
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
    background: white;
    padding: 24px;
    border-radius: 12px;
    box-shadow:
        0 4px 12px rgba(0,0,0,.08);
}}

section {{
    margin-top: 60px;
}}

.cta {{
    background: #2563eb;
    color: white;
    padding: 30px;
    border-radius: 12px;
    text-align: center;
}}

</style>

</head>

<body>

<header>

<h1>{html.escape(hero_title)}</h1>

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

