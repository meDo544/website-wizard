from __future__ import annotations

from collections.abc import Callable
from typing import Any

from backend.services.templates.base import (
    render_template as render_base_template,
)

from backend.services.templates.classic import (
    render_template as render_classic_template,
)

TemplateRenderer = Callable[..., str]


TEMPLATE_REGISTRY: dict[str, TemplateRenderer] = {
    "modern": render_base_template,
    "classic": render_classic_template,
    "minimal": render_base_template,
    "luxury": render_base_template,
}


def normalize_template_name(
    template_name: str | None,
) -> str:

    if not template_name:
        return "modern"

    normalized = (
        str(template_name)
        .strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )

    if normalized not in TEMPLATE_REGISTRY:
        return "modern"

    return normalized


def get_template_renderer(
    template_name: str | None,
) -> TemplateRenderer:

    normalized = normalize_template_name(
        template_name
    )

    return TEMPLATE_REGISTRY[normalized]


def render_selected_template(
    *,
    template_name: str | None,
    title: str,
    tagline: str,
    hero_title: str,
    hero_subtitle: str,
    seo_title: str,
    seo_description: str,
    content_html: str,
    theme: str = "modern",
    branding: dict[str, Any] | None = None,
) -> str:

    renderer = get_template_renderer(
        template_name
    )

    return renderer(
        title=title,
        tagline=tagline,
        hero_title=hero_title,
        hero_subtitle=hero_subtitle,
        seo_title=seo_title,
        seo_description=seo_description,
        content_html=content_html,
        theme=theme,
        branding=branding,
    )
