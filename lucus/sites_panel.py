"""
Admin header: switch ``django.contrib.sites`` context for shared multi-site admin.

Session key ``lucus_admin_site_id`` stores the chosen primary key. Use
``get_admin_site_for_request(request)`` (or enable ``LucusAdminSiteMiddleware``) so
``request.site`` in ``/admin/`` matches the selection.

Settings
--------
LUCUS_ADMIN_SITE_SELECTOR
    ``False`` — hide the header control and ignore the session override.
    Omitted — enable when ``django.contrib.sites`` is installed and there are
    at least two ``Site`` rows.
"""

from __future__ import annotations

from typing import Any

from django.conf import settings
from django.db import OperationalError, ProgrammingError
from django.http import HttpRequest

SESSION_KEY = "lucus_admin_site_id"


def sites_app_enabled() -> bool:
    return "django.contrib.sites" in settings.INSTALLED_APPS


def sites_selector_enabled() -> bool:
    if getattr(settings, "LUCUS_ADMIN_SITE_SELECTOR", None) is False:
        return False
    return sites_app_enabled()


def get_admin_site_for_request(request: HttpRequest):
    """
    Resolve the active ``Site`` for this request (admin session override or ``SITE_ID``).

    When the header selector is disabled, returns ``request.site`` if present,
    otherwise the default site from settings.
    """
    from django.contrib.sites.models import Site

    def _first_site():
        try:
            return Site.objects.order_by("pk").first()
        except (OperationalError, ProgrammingError):
            return None

    def _get(pk) -> Site | None:
        try:
            return Site.objects.get(pk=pk)
        except (Site.DoesNotExist, OperationalError, ProgrammingError):
            return None

    if not sites_app_enabled():
        if hasattr(request, "site") and request.site is not None:
            return request.site
        sid = getattr(settings, "SITE_ID", None)
        if sid is not None:
            s = _get(sid)
            if s is not None:
                return s
        return _first_site()

    if not sites_selector_enabled():
        if hasattr(request, "site") and request.site is not None:
            return request.site
        sid = getattr(settings, "SITE_ID", None)
        if sid is not None:
            s = _get(sid)
            if s is not None:
                return s
        return _first_site()

    raw = request.session.get(SESSION_KEY)
    if raw is not None:
        try:
            pk = int(raw)
            s = _get(pk)
            if s is not None:
                return s
        except ValueError:
            pass

    sid = getattr(settings, "SITE_ID", None)
    if sid is not None:
        s = _get(sid)
        if s is not None:
            return s
    return _first_site()


def admin_sites_toolbar_context(request: HttpRequest) -> dict[str, Any]:
    """Context for ``admin/base.html`` toolbar (empty when selector should not show)."""
    if not sites_selector_enabled():
        return {
            "lucus_admin_site_choices": (),
            "lucus_selected_site_id": None,
        }

    from django.contrib.sites.models import Site

    try:
        sites = list(Site.objects.order_by("domain", "pk").only("id", "domain", "name"))
    except (OperationalError, ProgrammingError):
        return {
            "lucus_admin_site_choices": (),
            "lucus_selected_site_id": None,
        }

    if len(sites) < 2:
        return {
            "lucus_admin_site_choices": (),
            "lucus_selected_site_id": None,
        }

    choices: list[tuple[int, str]] = []
    for s in sites:
        label = s.name.strip() if (s.name or "").strip() else s.domain
        if s.domain and s.name and s.name.strip() != s.domain:
            label = f"{s.name} ({s.domain})"
        choices.append((s.pk, label))

    try:
        current = get_admin_site_for_request(request)
    except Exception:
        current = None
    selected = current.pk if current is not None else None

    return {
        "lucus_admin_site_choices": tuple(choices),
        "lucus_selected_site_id": selected,
    }


class LucusAdminSiteMiddleware:
    """
    For paths starting with ``/admin/``, set ``request.site`` from
    ``get_admin_site_for_request`` (after ``SessionMiddleware``).

    Add to ``MIDDLEWARE`` after ``django.contrib.sites.middleware.CurrentSiteMiddleware``
    if you use it; otherwise after ``SessionMiddleware`` is enough.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        if sites_selector_enabled() and request.path.startswith("/admin/"):
            try:
                request.site = get_admin_site_for_request(request)
            except Exception:
                pass
        return self.get_response(request)
