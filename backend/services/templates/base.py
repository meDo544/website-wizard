import html


def render_template(
    title: str,
    tagline: str,
    prompt: str,
    content_html: str,
) -> str:

    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>{html.escape(title)}</title>

<style>

body {{
    font-family: Arial, sans-serif;
    margin: 0;
    background: #f8fafc;
}}

header {{
    background: #2563eb;
    color: white;
    padding: 60px;
    text-align: center;
}}

main {{
    max-width: 1100px;
    margin: auto;
    padding: 40px;
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
    padding: 20px;
    border-radius: 12px;
}}

.prompt-box {{
    margin-top: 40px;
    background: white;
    padding: 20px;
    border-radius: 12px;
}}

</style>

</head>

<body>

<header>

<h1>{html.escape(title)}</h1>

<p>{html.escape(tagline)}</p>

</header>

<main>

{content_html}

<div class="prompt-box">
<h2>Generated From Prompt</h2>
<p>{html.escape(prompt)}</p>
</div>

</main>

</body>

</html>
"""

