"""
Post-process ``AdminSite.get_app_list`` for the admin nav sidebar: merge model
entries into target apps without changing admin URLs.
"""

from __future__ import annotations

from typing import Any

from django.utils.translation import gettext as _


def reorganize_admin_app_list(app_list: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Merge models across registered apps and set section display names.

    Args:
        app_list: Value returned by the default ``get_app_list``.

    Returns:
        Filtered and merged app list for the sidebar.
    """

    by_label: dict[str, dict[str, Any]] = {}

    for app in app_list:
        lbl = app.get("app_label") or ""

        if not lbl or lbl in by_label:
            continue

        by_label[lbl] = {**app, "models": list(app.get("models") or [])}

    merge_pairs = (
        ("redirects", "sites"),
        ("constance", "sites"),
        ("solo", "sites"),
        ("auditlog", "sites"),
        ("admin", "sites"),
        ("account", "auth"),
        ("socialaccount", "auth"),
        ("index", "articles"),
        ("siteconfig", "sites"),
        ("moderation", "comments"),
        ("django_summernote", "media"),
    )

    for src, tgt in merge_pairs:

        if src in by_label and tgt in by_label:
            by_label[tgt]["models"].extend(by_label[src]["models"])
            by_label[src]["models"] = []

    if "sites" in by_label and by_label["sites"]["models"]:
        by_label["sites"]["name"] = _("Сайт и настройки")

    if "comments" in by_label and by_label["comments"]["models"]:
        by_label["comments"]["name"] = _("Комментарии и модерация")

    if "auth" in by_label and by_label["auth"]["models"]:
        by_label["auth"]["name"] = _("Пользователи")

    for tgt in ("sites", "auth", "articles"):

        if tgt in by_label and by_label[tgt]["models"]:
            by_label[tgt]["models"].sort(key=lambda x: (x.get("name") or "").lower())

    out: list[dict[str, Any]] = []
    seen: set[str] = set()

    for app in app_list:
        lbl = app.get("app_label") or ""

        if not lbl or lbl in seen:
            continue

        block = by_label.get(lbl)

        if not block or not block["models"]:
            continue

        seen.add(lbl)
        out.append(block)

    return out


def patch_admin_get_app_list() -> None:
    """
    Replace ``admin.site.get_app_list`` with a wrapper that calls
    ``reorganize_admin_app_list`` for the full-app list. Idempotent.
    """

    from django.contrib import admin

    if getattr(admin.site, "_lucus_sidebar_patched", False):
        return

    original = admin.site.get_app_list
    admin.site._lucus_original_get_app_list = original

    def get_app_list(request, app_label=None):
        base = original(request, app_label=app_label)

        if app_label is not None:
            return base

        return reorganize_admin_app_list(base)

    admin.site.get_app_list = get_app_list  # type: ignore[method-assign]
    admin.site._lucus_sidebar_patched = True
