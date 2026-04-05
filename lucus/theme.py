"""
Lucus admin theme: bundled color schemes, per-user preferences, extra CSS.

Settings
--------
LUCUS_EXTRA_STATIC_CSS
    Iterable of paths relative to staticfiles roots, or a single string.
    Loaded after the scheme stylesheet. Paths must not contain ``..`` or
    start with ``/``; allowed characters: letters, digits, ``_``, ``.``, ``/``, ``-``.

    LUCUS_UI
        Optional dict of UI feature flags (all default ``True`` if omitted):

        - ``help_as_icon`` — field ``help_text`` behind a “?” ``<details>`` control.
        - ``high_contrast_toggle`` — show “High contrast” in the user menu (uses
          ``localStorage`` + ``data-lucus-contrast="high"`` on ``<html>``).

        Change-form save/delete bar and changelist actions bar are fixed to the
        viewport bottom.

Color scheme is chosen from bundled schemes (and optional extra entries) and
stored per user in ``LucusAdminUiPreference``. There is no ``LUCUS_COLOR_SCHEME``
setting: defaults come from the first bundled scheme until the user saves a choice.
"""

from __future__ import annotations

import re
from typing import Any

from django.conf import settings
from django.core.exceptions import FieldDoesNotExist
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _


def _user_model_declares_avatar(model: type) -> bool:
    try:
        model._meta.get_field("avatar")
        return True
    except FieldDoesNotExist:
        pass
    desc = model.__dict__.get("avatar")
    if isinstance(desc, property):
        return True
    try:
        from django.utils.functional import cached_property as django_cached_property
    except ImportError:
        django_cached_property = None
    if django_cached_property is not None and isinstance(desc, django_cached_property):
        return True
    functools_cached = getattr(__import__("functools", fromlist=["cached_property"]), "cached_property", None)
    if functools_cached is not None and isinstance(desc, functools_cached):
        return True
    return False


def _avatar_raw_to_url(request: HttpRequest, raw: Any) -> str | None:
    if raw is None or raw is False:
        return None
    if hasattr(raw, "url"):
        try:
            u = raw.url
        except (ValueError, OSError):
            return None
        if not u:
            return None
    else:
        u = str(raw).strip()
        if not u:
            return None
    if u.startswith("/"):
        return request.build_absolute_uri(u)
    return u


def lucus_user_avatar_url(request: HttpRequest) -> str | None:
    """
    URL for the admin header avatar image if the user model defines ``avatar``
    (model field or ``@property`` / ``cached_property``) and the value is non-empty.
    """
    user = getattr(request, "user", None)
    if user is None or not getattr(user, "is_authenticated", False):
        return None
    model = user.__class__
    if not _user_model_declares_avatar(model):
        return None
    try:
        raw = getattr(user, "avatar")
    except Exception:
        return None
    return _avatar_raw_to_url(request, raw)

_SCHEME_RE = re.compile(r"^[a-z0-9_-]{1,64}$", re.I)
_EXTRA_RE = re.compile(r"^[a-zA-Z0-9_./-]+$")

# Bundled palette files under static/lucus/css/<slug>.css
BUNDLED_COLOR_SCHEMES: tuple[tuple[str, str], ...] = (
    ("olivia", _("Olivia")),
    ("grey", _("Grey")),
    ("slate", _("Slate")),
    ("dune", _("Dune")),
    ("midnight", _("Midnight")),
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

    return {
        "lucus_scheme_stylesheet": f"lucus/css/{scheme}.css",
        "lucus_extra_stylesheets": _extra_stylesheets(),
        "lucus_color_scheme_choices": BUNDLED_COLOR_SCHEMES,
        "lucus_selected_color_scheme": scheme,
        "lucus_appearance_choices": APPEARANCE_CHOICES,
        "lucus_selected_appearance": appearance,
        "lucus_ui_help_as_icon": _ui_flag(ui_raw, "help_as_icon", True),
        "lucus_ui_high_contrast_toggle": _ui_flag(ui_raw, "high_contrast_toggle", True),
        "lucus_user_avatar_url": lucus_user_avatar_url(request),
    }
