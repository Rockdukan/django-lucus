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


def _paths_for_prefix_match(request: HttpRequest) -> tuple[str, ...]:
    """
    Paths to test against ``LUCUS_STAFF_THEME_PATH_PREFIXES``.

    - ``request.path`` is normally ``PATH_INFO`` (without ``SCRIPT_NAME``), but some
      stacks put the full URI path on ``path``; strip a leading ``SCRIPT_NAME`` if
      present.
    - With ``LocaleMiddleware``, the first segment can be a language code
      (``/en/rosetta/…``); also try the path without that segment.
    """
    raw = getattr(request, "path", "") or "/"
    meta = getattr(request, "META", None) or {}
    script = (meta.get("SCRIPT_NAME") or "").strip()
    candidates: list[str] = []
    path = raw
    if script:
        script = "/" + script.strip("/")
        if path.startswith(script):
            path = path[len(script) :] or "/"
            if not path.startswith("/"):
                path = "/" + path
    candidates.append(path)
    segs = [s for s in path.strip("/").split("/") if s]
    if segs and getattr(settings, "USE_I18N", False):
        codes = {str(c).lower() for c, _ in getattr(settings, "LANGUAGES", ()) if c}
        if segs[0].lower() in codes and len(segs) > 1:
            tail = "/" + "/".join(segs[1:])
            if tail not in candidates:
                candidates.append(tail)
    return tuple(candidates)


def _path_matches_prefixes(request: HttpRequest, prefixes: tuple[str, ...]) -> bool:
    for path in _paths_for_prefix_match(request):
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
    from lucus.theme import lucus_admin_extra_context

    site = _lucus_admin_site_instances()[0]
    ctx = site.each_context(request)
    ctx.update(lucus_admin_extra_context(request))
    return ctx
