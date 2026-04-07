from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

from django.contrib import admin
from django.conf import settings
from django.urls import NoReverseMatch, reverse
from django.utils.translation import gettext_lazy as _


@dataclass(frozen=True)
class DashboardLink:
    label: Any
    url: str


@dataclass(frozen=True)
class DashboardSection:
    title: Any
    links: tuple[DashboardLink, ...]


@dataclass(frozen=True)
class DashboardColumn:
    sections: tuple[DashboardSection, ...]
    classes: str = (
        "lucus-dashboard__col lucus-grid__col lucus-grid__col--3 "
        "lucus-grid__col--md-6 lucus-grid__col--sm-12 lucus-grid__col--xs-12"
    )


def _normalize_admin_path(url: str) -> str:
    """Normalize an admin URL to a single path form for set membership (trailing slash)."""
    if not url:
        return ""
    path = urlparse(url).path or "/"
    return path if path.endswith("/") else path + "/"


def safe_reverse(admin_urlname: str) -> str | None:
    """Return reversed admin URL or ``None`` if the name does not resolve."""
    try:
        return reverse(admin_urlname)
    except NoReverseMatch:
        return None


def normalize_config(raw: Iterable[dict[str, Any]]) -> tuple[DashboardColumn, ...]:
    """Normalize layout-style ``LUCUS_DASHBOARD`` into ``DashboardColumn`` tuples."""
    raw_list = list(raw)
    has_explicit_columns = any(isinstance(col, dict) and ("column" in col) for col in raw_list)

    def parse_column_value(col: dict[str, Any]) -> int | None:
        v = col.get("column")
        if v is None:
            return None
        try:
            return int(v)
        except (TypeError, ValueError):
            return None

    if has_explicit_columns:
        by_col: dict[int, list[dict[str, Any]]] = {}
        max_col = 1
        for col in raw_list:
            if not isinstance(col, dict):
                continue
            c = parse_column_value(col)
            if c is None:
                continue
            c = max(1, min(c, 4))
            by_col.setdefault(c, []).append(col)
            max_col = max(max_col, c)

        max_col = 4
        cols: list[DashboardColumn] = []

        def build_sections(merged_section_dicts: list[dict[str, Any]]) -> list[DashboardSection]:
            out: list[DashboardSection] = []
            for sec in merged_section_dicts:
                links: list[DashboardLink] = []
                for link in sec.get("links", []):
                    url = link.get("url")
                    if not url and link.get("admin_urlname"):
                        url = safe_reverse(link["admin_urlname"])
                    if not url:
                        continue
                    links.append(DashboardLink(label=link.get("label", ""), url=url))
                if links:
                    out.append(DashboardSection(title=sec.get("title", ""), links=tuple(links)))
            return out

        for col_idx in range(1, max_col + 1):
            col_dicts = by_col.get(col_idx, [])
            if not col_dicts:
                merged_raw: list[dict[str, Any]] = []
                classes = DashboardColumn.classes
            else:
                merged_raw = []
                for cd in col_dicts:
                    merged_raw.extend(cd.get("sections", []))
                classes = col_dicts[0].get("classes") or DashboardColumn.classes

            sections = build_sections(merged_raw)
            cols.append(DashboardColumn(sections=tuple(sections), classes=classes))

        return tuple(cols)

    cols: list[DashboardColumn] = []
    for col in raw_list:
        if not isinstance(col, dict):
            continue
        classes = col.get("classes") or DashboardColumn.classes
        sections: list[DashboardSection] = []
        for sec in col.get("sections", []):
            links: list[DashboardLink] = []
            for link in sec.get("links", []):
                url = link.get("url")
                if not url and link.get("admin_urlname"):
                    url = safe_reverse(link["admin_urlname"])
                if not url:
                    continue
                links.append(DashboardLink(label=link.get("label", ""), url=url))
            if links:
                sections.append(DashboardSection(title=sec.get("title", ""), links=tuple(links)))
        if sections:
            cols.append(DashboardColumn(sections=tuple(sections), classes=classes))
    return tuple(cols)


def links_for_apps(
    app_list: list[dict[str, Any]],
    app_labels: set[str] | Sequence[str] | frozenset[str],
    *,
    label_overrides: dict[tuple[str, str], Any] | None = None,
) -> tuple[DashboardLink, ...]:
    """
    Build dashboard links for the given ``app_labels`` using admin ``app_list``.

    For ``list`` / ``tuple``, apps follow config order; for ``set`` / ``frozenset``,
    order follows ``app_list``. ``label_overrides`` maps ``(app_label, object_name)``
    to display labels.
    """
    links: list[DashboardLink] = []

    def append_models(app_item: dict[str, Any]) -> None:
        for m in (app_item.get("models") or []):
            url = m.get("admin_url")
            if url:
                app_label = app_item.get("app_label") or ""
                obj_name = m.get("object_name") or ""
                label = m.get("name", "")
                if label_overrides and (app_label, obj_name) in label_overrides:
                    label = label_overrides[(app_label, obj_name)]
                links.append(DashboardLink(label=label, url=url))

    if isinstance(app_labels, (set, frozenset)):
        labels_set = app_labels
        for app_item in app_list:
            if (app_item.get("app_label") or "") not in labels_set:
                continue
            append_models(app_item)
    else:
        seen_lab: set[str] = set()
        order: list[str] = []
        for lab in app_labels:
            if not lab or lab in seen_lab:
                continue
            seen_lab.add(lab)
            order.append(lab)
        by_label = {(a.get("app_label") or ""): a for a in app_list}
        for lab in order:
            app_item = by_label.get(lab)
            if app_item:
                append_models(app_item)

    return tuple(links)


def _covered_admin_paths_from_dashboard_columns(
    columns: tuple[DashboardColumn, ...],
) -> set[str]:
    """Normalized changelist paths already present on the dashboard (per-model coverage)."""
    covered: set[str] = set()
    for col in columns:
        for sec in col.sections:
            for link in sec.links:
                p = _normalize_admin_path(link.url)
                if p:
                    covered.add(p)
    return covered


def _layout_dashboard_append_uncovered(
    request,
    columns: tuple[DashboardColumn, ...],
) -> tuple[DashboardColumn, ...]:
    """
    For layout-style ``LUCUS_DASHBOARD`` (``sections`` / ``normalize_config``),
    append any admin apps not referenced by existing links into the **last**
    column — same idea as ``grouped_dashboard_from_app_list`` +
    ``LUCUS_DASHBOARD_APPEND_UNCOVERED``.
    """
    if not getattr(settings, "LUCUS_DASHBOARD_APPEND_UNCOVERED", True):
        return columns

    app_list = _raw_admin_app_list(request)
    covered_paths = _covered_admin_paths_from_dashboard_columns(columns)
    extras: list[DashboardSection] = []

    for app_item in app_list:
        app_label = app_item.get("app_label") or ""
        if not app_label:
            continue
        links: list[DashboardLink] = []
        for m in app_item.get("models") or []:
            url = m.get("admin_url")
            if url and _normalize_admin_path(url) not in covered_paths:
                links.append(DashboardLink(label=m.get("name", ""), url=url))
        if links:
            extras.append(
                DashboardSection(title=app_item.get("name", ""), links=tuple(links))
            )

    if not extras:
        return columns
    if not columns:
        return (DashboardColumn(sections=tuple(extras)),)

    last = columns[-1]
    return columns[:-1] + (
        DashboardColumn(
            sections=last.sections + tuple(extras),
            classes=last.classes,
        ),
    )


def looks_like_dashboard_layout(raw: Any) -> bool:
    """True if ``raw`` looks like ``[{ "classes"?, "sections": [...] }, ...]``."""
    if not isinstance(raw, (list, tuple)) or not raw:
        return False
    first = raw[0]
    return isinstance(first, dict) and ("classes" in first or "sections" in first)


def looks_like_groups_config(raw: Any) -> bool:
    """True if first entry has ``column`` and ``app_labels`` and/or ``links``."""
    if not isinstance(raw, (list, tuple)) or not raw:
        return False
    first = raw[0]
    return (
        isinstance(first, dict)
        and "column" in first
        and ("app_labels" in first or "links" in first)
    )


def normalize_group_columns(groups: Iterable[dict[str, Any]]) -> tuple[dict[str, Any], ...]:
    """Clamp each group's ``column`` to at least 1 (1-based index)."""
    groups_list = list(groups)
    normalized: list[dict[str, Any]] = []
    for g in groups_list:
        col = int(g.get("column", 1) or 1)
        if col < 1:
            col = 1
        normalized.append({**g, "column": col})
    return tuple(normalized)


def _raw_admin_app_list(request):
    """Return ``get_app_list`` for the dashboard."""
    return admin.site.get_app_list(request)


def grouped_dashboard_from_app_list(
    request,
    *,
    groups: Iterable[dict[str, Any]] | None = None,
) -> tuple[DashboardColumn, ...]:
    """Build grouped dashboard columns from ``get_app_list`` and optional ``groups``."""
    app_list = _raw_admin_app_list(request)

    groups = (
        groups
        or getattr(settings, "LUCUS_DASHBOARD", None)
        or [
            {
                "column": 3,
                "title": "👤  Authorization",
                "links": [
                    {
                        "label": "Users",
                        "admin_urlname": "admin:auth_user_changelist",
                    },
                    {
                        "label": "Groups",
                        "admin_urlname": "admin:auth_group_changelist",
                    },
                ],
            },
        ]
    )

    groups = normalize_group_columns(groups)

    col_count = max(4, max((int(g.get("column", 1) or 1) for g in groups), default=1))
    cols: list[list[DashboardSection]] = [[] for _ in range(col_count)]

    label_overrides: dict[tuple[str, str], Any] = {
        ("constance", "Config"): _("Константы"),
    }

    # Only apps whose group actually rendered a non-empty section count as
    # ``app_labels``-covered for APPEND_UNCOVERED. Empty groups must not hide apps.
    rendered_explicit_app_labels: set[str] = set()

    for g in groups:
        seen_urls: set[str] = set()
        merged: list[DashboardLink] = []
        for link in g.get("links") or []:
            url = link.get("url")
            if not url and link.get("admin_urlname"):
                url = safe_reverse(link["admin_urlname"])
            if not url or url in seen_urls:
                continue
            seen_urls.add(url)
            merged.append(DashboardLink(label=link.get("label", ""), url=url))
        raw_labels = g.get("app_labels")
        if raw_labels is None:
            label_arg: set[str] | Sequence[str] = frozenset()
        elif isinstance(raw_labels, (set, frozenset)):
            label_arg = raw_labels
        else:
            label_arg = raw_labels
        for dl in links_for_apps(app_list, label_arg, label_overrides=label_overrides):
            if dl.url not in seen_urls:
                seen_urls.add(dl.url)
                merged.append(dl)
        links_tuple = tuple(merged)

        if not links_tuple:
            continue

        cols[int(g.get("column", 1)) - 1].append(
            DashboardSection(title=g.get("title", ""), links=links_tuple)
        )
        if raw_labels is not None:
            if isinstance(raw_labels, (set, frozenset)):
                rendered_explicit_app_labels.update(raw_labels)
            elif isinstance(raw_labels, (list, tuple)):
                rendered_explicit_app_labels.update(raw_labels)

    if getattr(settings, "LUCUS_DASHBOARD_APPEND_UNCOVERED", True):
        explicit_covered_apps: set[str] = set(rendered_explicit_app_labels)
        covered_paths: set[str] = set()
        for g in groups:
            for link in g.get("links") or []:
                url = link.get("url")
                if not url and link.get("admin_urlname"):
                    url = safe_reverse(link["admin_urlname"])
                if url:
                    p = _normalize_admin_path(url)
                    if p:
                        covered_paths.add(p)
        for sec_tup in cols:
            for sec in sec_tup:
                for dl in sec.links:
                    p = _normalize_admin_path(dl.url)
                    if p:
                        covered_paths.add(p)

        for app_item in app_list:
            app_label = (app_item.get("app_label") or "")
            if not app_label or app_label in explicit_covered_apps:
                continue
            links = []
            for m in (app_item.get("models") or []):
                url = m.get("admin_url")
                if url and _normalize_admin_path(url) not in covered_paths:
                    links.append(DashboardLink(label=m.get("name", ""), url=url))
            if links:
                cols[-1].append(DashboardSection(title=app_item.get("name", ""), links=tuple(links)))

    return tuple(DashboardColumn(sections=tuple(secs)) for secs in cols if secs)


def get_dashboard_for_request(request) -> tuple[DashboardColumn, ...]:
    """
    Build dashboard columns for the admin index.

    Reads ``settings.LUCUS_DASHBOARD`` (layout or column groups). Groups may mix
    ``links`` and ``app_labels``; duplicate URLs are omitted. If
    ``LUCUS_DASHBOARD_APPEND_UNCOVERED`` is true, apps not covered by groups are
    appended to the last column. If ``LUCUS_DASHBOARD`` is absent, falls back to
    grouped defaults from ``get_app_list``.
    """

    raw = getattr(settings, "LUCUS_DASHBOARD", None)

    if raw and looks_like_dashboard_layout(raw):
        cols = normalize_config(raw)
        return _layout_dashboard_append_uncovered(request, cols)

    if raw and looks_like_groups_config(raw):
        return grouped_dashboard_from_app_list(request, groups=raw)

    return grouped_dashboard_from_app_list(request)

