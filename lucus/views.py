from __future__ import annotations

from urllib.parse import urlsplit, urlunsplit

from django.http import HttpResponseRedirect
from django.views.decorators.http import require_POST

from lucus.models import LucusAdminUiPreference
from lucus.theme import bundled_scheme_slugs, is_valid_scheme_slug, normalize_appearance


def _safe_redirect_url(next_raw: str, fallback: str) -> str:
    if not next_raw:
        return fallback
    u = urlsplit(next_raw)
    if u.scheme or u.netloc:
        return fallback
    if not u.path.startswith("/"):
        return fallback
    return urlunsplit(("", "", u.path, u.query, u.fragment)) or fallback


@require_POST
def save_admin_ui(request):
    """Persist color scheme + appearance for the current user (staff-only via admin_view wrapper)."""
    next_url = _safe_redirect_url(
        request.POST.get("next", ""),
        request.META.get("HTTP_REFERER") or "/admin/",
    )
    scheme = (request.POST.get("color_scheme") or "").strip().lower()
    if not is_valid_scheme_slug(scheme):
        scheme = bundled_scheme_slugs()[0]
    appearance = normalize_appearance(request.POST.get("appearance"))
    LucusAdminUiPreference.objects.update_or_create(
        user=request.user,
        defaults={"color_scheme": scheme, "appearance": appearance},
    )
    resp = HttpResponseRedirect(next_url)
    age = 365 * 24 * 60 * 60
    resp.set_cookie("lucus_color_scheme", scheme, max_age=age, samesite="Lax", path="/")
    resp.set_cookie("lucus_appearance", appearance, max_age=age, samesite="Lax", path="/")
    return resp
