"""
Lucus theme + admin chrome for staff pages that use ``admin/base*.html`` but are not
wrapped by ``AdminSite.admin_view`` (e.g. django-log-viewer at ``/logs/``).
"""

from __future__ import annotations

from typing import Any

from django.conf import settings
from django.http import HttpRequest

# Not "/admin/": ModelAdmin views already receive each_context from AdminSite.
_DEFAULT_PATH_PREFIXES: tuple[str, ...] = (
    "/logs/",
    "/rosetta/",
    "/explorer/",
)


def _path_matches_prefixes(request: HttpRequest, prefixes: tuple[str, ...]) -> bool:
    path = getattr(request, "path", "") or "/"
    for p in prefixes:
        base = p.rstrip("/")
        if not base:
            continue
        if path == base or path.startswith(base + "/"):
            return True
    return False


def staff_integrations_theme(request: HttpRequest) -> dict[str, Any]:
    """
    Merge default ``AdminSite.each_context`` (including Lucus patches) when a staff
    user hits URL prefixes listed in ``LUCUS_STAFF_THEME_PATH_PREFIXES``.

    Set ``LUCUS_STAFF_THEME_PATH_PREFIXES = ()`` to disable.
    """
    user = getattr(request, "user", None)
    if (
        user is None
        or not getattr(user, "is_authenticated", False)
        or not getattr(user, "is_staff", False)
    ):
        return {}

    raw = getattr(settings, "LUCUS_STAFF_THEME_PATH_PREFIXES", None)
    if isinstance(raw, str):
        prefixes: tuple[str, ...] = (raw,)
    elif isinstance(raw, (list, tuple)):
        prefixes = tuple(raw)
    elif raw is None:
        prefixes = _DEFAULT_PATH_PREFIXES
    else:
        prefixes = _DEFAULT_PATH_PREFIXES

    if not prefixes:
        return {}

    if not _path_matches_prefixes(request, prefixes):
        return {}

    from lucus.apps import _lucus_admin_site_instances

    site = _lucus_admin_site_instances()[0]
    return site.each_context(request)
