"""
Lucus admin theme: bundled color schemes, per-user preferences, extra CSS.

Settings
--------
LUCUS_EXTRA_STATIC_CSS
    Iterable of paths relative to staticfiles roots, or a single string.
    Loaded after the scheme stylesheet. Paths must not contain ``..`` or
    start with ``/``; allowed characters: letters, digits, ``_``, ``.``, ``/``, ``-``.

LUCUS_ADMIN_BACKGROUND_IMAGE
    Optional full-page background for the admin (skipped in popups). Rendered as an
    ``<img>`` (not CSS ``url()``) so special characters and HTML escaping do not break
    the image. Values:

    - Absolute URL: ``https://…``, ``http://…``, or protocol-relative ``//…``.
    - Site-absolute path: starts with ``/`` (e.g. media or static URL path).
    - Static files path: relative to static roots, e.g. ``lucus/img/admin-bg.jpg``
      (passed to Django’s ``static()`` helper).

LUCUS_ADMIN_BACKGROUND_SCRIM_OPACITY
    Float ``0.0``…``1.0``. Opacity of the theme-colored overlay on top of the
    image for readability (default ``0.88``). Lower = more visible photo.
    Rendered for CSS with a dot decimal separator (comma would invalidate
    ``opacity`` under localized templates).

LUCUS_ADMIN_LANGUAGE_SELECTOR
    If ``False``, the header language ``<select>`` is never shown. If omitted
    (default), it is shown only when multilingual admin switching makes sense:
    ``USE_I18N`` is true, ``len(LANGUAGES) > 1``,
    ``LocaleMiddleware`` is installed, and the named URL ``set_language`` resolves
    (``django.conf.urls.i18n`` included).

LUCUS_ADMIN_SITE_SELECTOR
    If ``False``, the header ``django.contrib.sites`` switcher is hidden and the
    session key is ignored by ``get_admin_site_for_request``. If omitted, the
    switcher appears when ``django.contrib.sites`` is installed and there are at
    least two ``Site`` rows. Use ``lucus.sites_panel.LucusAdminSiteMiddleware``
    (after ``SessionMiddleware``) so ``request.site`` in ``/admin/`` matches the
    selection.

    LUCUS_UI
        Optional dict of UI feature flags:

        - ``help_as_icon`` — field ``help_text`` behind a “?” ``<details>`` control
          (default ``True`` if omitted).
        - ``high_contrast_toggle`` — show “High contrast” in the user menu (uses
          ``localStorage`` + ``data-lucus-contrast="high"`` on ``<html>``;
          default ``False`` if omitted).

        Change-form save/delete bar and changelist actions bar are fixed to the
        viewport bottom.

Color scheme is chosen from bundled schemes (and optional extra entries) and
stored per user in ``LucusAdminUiPreference``. There is no ``LUCUS_COLOR_SCHEME``
setting: defaults come from the first bundled scheme until the user saves a choice.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from django.conf import settings
from django.http import HttpRequest

from lucus.sites_panel import admin_sites_toolbar_context
from django.templatetags.static import static as static_url
from django.utils.translation import gettext_lazy as _

_SCHEME_RE = re.compile(r"^[a-z0-9_-]{1,64}$", re.I)
_EXTRA_RE = re.compile(r"^[a-zA-Z0-9_./+%-]+$")

# Bundled palette files under static/lucus/css/<slug>.css
BUNDLED_COLOR_SCHEMES: tuple[tuple[str, str], ...] = (
    ("olivia", _("Olivia")),
    ("grey", _("Grey")),
    ("slate", _("Slate")),
    ("dune", _("Dune")),
    ("midnight", _("Midnight")),
    ("nord", _("Nord")),
    ("dracula", _("Dracula")),
    ("github", _("GitHub")),
    ("catppuccin", _("Catppuccin")),
    ("tokyo", _("Tokyo Night")),
)

APPEARANCE_CHOICES: tuple[tuple[str, str], ...] = (
    ("light", _("Light")),
    ("dark", _("Dark")),
    ("auto", _("Auto")),
)


def bundled_scheme_slugs() -> list[str]:
    return [s[0] for s in BUNDLED_COLOR_SCHEMES]


def is_valid_scheme_slug(slug: str) -> bool:
    if not isinstance(slug, str) or not _SCHEME_RE.match(slug):
        return False
    return slug in bundled_scheme_slugs()


def normalize_appearance(raw: str | None) -> str:
    v = (raw or "auto").strip().lower()
    if v in ("light", "dark", "auto"):
        return v
    return "auto"


def _admin_background_image_url() -> str | None:
    raw = getattr(settings, "LUCUS_ADMIN_BACKGROUND_IMAGE", "") or ""
    if isinstance(raw, Path):
        raw = str(raw)
    if not isinstance(raw, str):
        return None
    raw = raw.strip()
    if not raw or ".." in raw:
        return None
    lower = raw.lower()
    if lower.startswith(("http://", "https://", "//")):
        return raw
    if raw.startswith("/"):
        return raw
    if not _EXTRA_RE.match(raw):
        return None
    return static_url(raw)


_LOCALE_MIDDLEWARE = "django.middleware.locale.LocaleMiddleware"


def _admin_set_language_url() -> str | None:
    """
    POST target for the header language switch, or None if the selector should be hidden.
    """
    if getattr(settings, "LUCUS_ADMIN_LANGUAGE_SELECTOR", None) is False:
        return None
    if not getattr(settings, "USE_I18N", True):
        return None
    langs = getattr(settings, "LANGUAGES", ())
    if not isinstance(langs, (list, tuple)) or len(langs) <= 1:
        return None
    middleware = getattr(settings, "MIDDLEWARE", None) or []
    if _LOCALE_MIDDLEWARE not in middleware:
        return None
    from django.urls import reverse

    try:
        return reverse("set_language")
    except Exception:
        # Must never break lucus_admin_extra_context (background, theme, …).
        return None


def _admin_background_scrim_opacity() -> float:
    raw = getattr(settings, "LUCUS_ADMIN_BACKGROUND_SCRIM_OPACITY", 0.88)
    try:
        v = float(raw)
    except (TypeError, ValueError):
        return 0.88
    return max(0.0, min(1.0, v))


def _admin_background_scrim_opacity_css() -> str:
    """
    Opacity for inline CSS. Must use a dot (0.5), never a comma — ru locale turns
    ``{{ float }}`` into ``0,5``, which is invalid in CSS and drops the property,
    leaving the scrim fully opaque and hiding the wallpaper image.
    """
    v = _admin_background_scrim_opacity()
    s = f"{v:.8f}".rstrip("0").rstrip(".")
    return s or "0"


def _extra_stylesheets() -> list[str]:
    raw = getattr(settings, "LUCUS_EXTRA_STATIC_CSS", ()) or ()
    if isinstance(raw, str):
        raw = (raw,)
    extra: list[str] = []
    if isinstance(raw, (list, tuple)):
        for p in raw:
            if (
                isinstance(p, str)
                and p
                and ".." not in p
                and not p.startswith("/")
                and _EXTRA_RE.match(p)
            ):
                extra.append(p)
    return extra


def _ui_flag(raw: dict[str, Any], key: str, default: bool = True) -> bool:
    if key not in raw:
        return default
    return bool(raw[key])


def _default_scheme_slug() -> str:
    return bundled_scheme_slugs()[0]


def resolve_scheme_and_appearance(request: HttpRequest) -> tuple[str, str]:
    from django.db import OperationalError, ProgrammingError

    from lucus.models import LucusAdminUiPreference

    scheme = _default_scheme_slug()
    appearance = "auto"
    user = getattr(request, "user", None)
    if user is not None and user.is_authenticated:
        try:
            pref = user.lucus_admin_ui_pref
        except (LucusAdminUiPreference.DoesNotExist, OperationalError, ProgrammingError):
            pref = None
        else:
            if is_valid_scheme_slug(pref.color_scheme):
                scheme = pref.color_scheme
            appearance = normalize_appearance(pref.appearance)
    else:
        ck_scheme = (request.COOKIES.get("lucus_color_scheme") or "").strip().lower()
        if is_valid_scheme_slug(ck_scheme):
            scheme = ck_scheme
        appearance = normalize_appearance(request.COOKIES.get("lucus_appearance"))
    return scheme, appearance


def lucus_admin_extra_context(request: HttpRequest) -> dict[str, Any]:
    scheme, appearance = resolve_scheme_and_appearance(request)

    ui_raw = getattr(settings, "LUCUS_UI", None) or {}
    if not isinstance(ui_raw, dict):
        ui_raw = {}

    bg_url = _admin_background_image_url()
    try:
        lang_url = _admin_set_language_url()
    except Exception:
        lang_url = None
    ctx = {
        "lucus_scheme_stylesheet": f"lucus/css/{scheme}.css",
        "lucus_extra_stylesheets": _extra_stylesheets(),
        "lucus_color_scheme_choices": BUNDLED_COLOR_SCHEMES,
        "lucus_selected_color_scheme": scheme,
        "lucus_appearance_choices": APPEARANCE_CHOICES,
        "lucus_selected_appearance": appearance,
        "lucus_ui_help_as_icon": _ui_flag(ui_raw, "help_as_icon", True),
        "lucus_ui_high_contrast_toggle": _ui_flag(ui_raw, "high_contrast_toggle", False),
        "lucus_admin_background_image_url": bg_url,
        "lucus_admin_background_scrim_opacity": _admin_background_scrim_opacity_css()
        if bg_url
        else None,
        "lucus_admin_set_language_url": lang_url,
    }
    ctx.update(admin_sites_toolbar_context(request))
    return ctx
