"""Template helpers for Lucus inline extensions."""

from __future__ import annotations

from django import template

register = template.Library()


@register.simple_tag
def lucus_sortable_excludes_csv(inline_opts) -> str:
    """Comma-separated field names excluded from “row has values” checks."""
    raw = getattr(inline_opts, "sortable_excludes", None)
    if not raw:
        return ""
    return ",".join(str(x) for x in raw)
