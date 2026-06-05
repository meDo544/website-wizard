from backend.services.templates.base import (
    render_template,
)


def generate(prompt: str) -> str:

    content_html = """
<h2>Featured Electronics</h2>

<div class="grid">

<div class="card">
<h3>AI Smart Speaker</h3>
<p>Voice-controlled smart home assistant.</p>
</div>

<div class="card">
<h3>AI Security Camera</h3>
<p>Facial recognition and smart alerts.</p>
</div>

<div class="card">
<h3>AI Drone</h3>
<p>Autonomous flight and navigation.</p>
</div>

</div>
"""

    return render_template(
        title="AI Electronics Shop",
        tagline="Smart devices for modern living.",
        prompt=prompt,
        content_html=content_html,
    )
