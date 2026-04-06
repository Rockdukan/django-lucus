"""Nav helpers for Lucus admin templates."""

from __future__ import annotations

from urllib.parse import urlparse

from django import template

register = template.Library()


@register.filter
def lucus_url_path(url) -> str:
    """Path component only (for matching ``request.path`` to menu links)."""
    if not url:
        return ""
    p = urlparse(str(url))
    return p.path or str(url)
