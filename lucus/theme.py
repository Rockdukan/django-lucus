"""
Admin static assets: color scheme slug and extra stylesheets from Django settings.

Settings:
    LUCUS_COLOR_SCHEME
        Basename for ``static/lucus/css/<value>.css``. Allowed characters:
        ASCII letters, digits, ``_``, ``-``; length 1–64. Default: ``"olivia"``.

    LUCUS_EXTRA_STATIC_CSS
        Iterable of paths relative to staticfiles roots, or a single string.
        Loaded after the scheme stylesheet. Paths must not contain ``..`` or
        start with ``/``; allowed characters: letters, digits, ``_``, ``.``, ``/``, ``-``.
"""

from __future__ import annotations

import re
from typing import Any

from django.conf import settings

_SCHEME_RE = re.compile(r"^[a-z0-9_-]{1,64}$", re.I)
_EXTRA_RE = re.compile(r"^[a-zA-Z0-9_./-]+$")


def lucus_admin_extra_context() -> dict[str, Any]:
    scheme = getattr(settings, "LUCUS_COLOR_SCHEME", "olivia") or "olivia"
    if not isinstance(scheme, str) or not _SCHEME_RE.match(scheme):
        scheme = "olivia"

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

    return {
        "lucus_scheme_stylesheet": f"lucus/css/{scheme}.css",
        "lucus_extra_stylesheets": extra,
    }
