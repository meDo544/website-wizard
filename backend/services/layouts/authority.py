from __future__ import annotations

import html
from typing import Any


def _get_selected_headline(
    profile: dict[str, Any],
    field_name: str,
) -> str:

    selected_item = profile.get(
        field_name,
        {},
    )

    if not isinstance(
        selected_item,
        dict,
    ):
        return ""

    return str(
        selected_item.get(
            "headline",
            "",
        )
    ).strip()


def render_layout(
    *,
    profile: dict[str, Any],
    sections: dict[str, str],
) -> str:
    """
    Render an authority-focused content layout.

    The authority layout places credibility,
    value, and trust signals before the standard
    business sections.
    """

    authority_headline = _get_selected_headline(
        profile,
        "selected_authority",
    )

    value_prop_headline = _get_selected_headline(
        profile,
        "selected_value_prop",
    )

    trust_headline = _get_selected_headline(
        profile,
        "selected_trust",
    )

    authority_blocks: list[str] = []

    if authority_headline:

        authority_blocks.append(
            f"""
            <section class="authority-proof">
                <h2>Professional Expertise</h2>
                <p>
                    {html.escape(authority_headline)}
                </p>
            </section>
            """
        )

    if value_prop_headline:

        authority_blocks.append(
            f"""
            <section class="authority-value">
                <h2>Why Clients Choose Us</h2>
                <p>
                    {html.escape(value_prop_headline)}
                </p>
            </section>
            """
        )

    if trust_headline:

        authority_blocks.append(
            f"""
            <section class="authority-trust">
                <h2>Trusted Guidance</h2>
                <p>
                    {html.escape(trust_headline)}
                </p>
            </section>
            """
        )

    authority_html = "\n".join(
        authority_blocks
    )

    preferred_order = [
        "testimonials",
        "services",
        "features",
        "faqs",
        "contact",
        "cta",
    ]

    ordered_sections: list[str] = []

    for section_name in preferred_order:

        section_html = sections.get(
            section_name,
            "",
        )

        if section_html:
            ordered_sections.append(
                section_html
            )

    for section_name, section_html in sections.items():

        if (
            section_name not in preferred_order
            and section_html
        ):
            ordered_sections.append(
                section_html
            )

    content_html = "\n".join(
        ordered_sections
    )

    return f"""
    <div
        class="layout layout-authority"
        data-layout="authority"
    >
        <div class="authority-introduction">
            {authority_html}
        </div>

        <div class="authority-content">
            {content_html}
        </div>
    </div>
    """
