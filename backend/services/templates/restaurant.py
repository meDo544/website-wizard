from backend.services.templates.base import (
    render_template,
)


def generate(prompt: str) -> str:

    content_html = """
<h2>Featured Menu</h2>

<div class="grid">

<div class="card">
<h3>Signature Steak</h3>
<p>Premium cuts cooked perfectly.</p>
</div>

<div class="card">
<h3>Seafood Platter</h3>
<p>Fresh seafood sourced daily.</p>
</div>

<div class="card">
<h3>Chef's Special</h3>
<p>Rotating gourmet creations.</p>
</div>

</div>
"""

    return render_template(
        title="AI Restaurant",
        tagline="Modern dining powered by technology.",
        prompt=prompt,
        content_html=content_html,
    )

