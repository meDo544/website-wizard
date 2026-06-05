from backend.services.templates.base import (
    render_template,
)


def generate(prompt: str) -> str:

    content_html = """
<h2>Featured Pizzas</h2>

<div class="grid">

<div class="card">
<h3>Pepperoni Supreme</h3>
<p>Premium pepperoni and mozzarella.</p>
</div>

<div class="card">
<h3>Veggie Delight</h3>
<p>Fresh vegetables and signature sauce.</p>
</div>

<div class="card">
<h3>AI Special Pizza</h3>
<p>Recommendations tailored to your taste.</p>
</div>

</div>
"""

    return render_template(
        title="AI Pizza Shop",
        tagline="Fresh artisan pizzas powered by AI.",
        prompt=prompt,
        content_html=content_html,
    )

