from __future__ import annotations

#
# Builtins
#
from dataclasses import dataclass
from typing import Any, Iterable

# Third-party
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
    classes: str = "lucus-dashboard__col lucus-col lucus-col-3 lucus-col-md-6 lucus-col-sm-12"


def safe_reverse(admin_urlname: str) -> str | None:
    """
    Безопасно получает URL по имени админского URL.

    Args:
        admin_urlname: Имя URL для админки, например `admin:app_model_changelist`.

    Returns:
        URL, если он существует, иначе `None`.
    """
    try:
        return reverse(admin_urlname)
    except NoReverseMatch:
        return None


def normalize_config(raw: Iterable[dict[str, Any]]) -> tuple[DashboardColumn, ...]:
    """
    Нормализует конфигурацию dashboard в колонке/секциях/линках.

    Args:
        raw: Входная конфигурация (обычно из `settings.LUCUS_DASHBOARD`).

    Returns:
        Колонки dashboard в едином формате.
    """
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

    # Если задано column: 1..4, сортируем и оставляем пустые колонки,
    # чтобы UI был предсказуемым.

    if has_explicit_columns:
        by_col: dict[int, dict[str, Any]] = {}
        max_col = 1
        for col in raw_list:
            if not isinstance(col, dict):
                continue
            c = parse_column_value(col)
            if c is None:
                continue
            c = max(1, c)
            by_col[c] = col
            max_col = max(max_col, c)

        # В UI везде подразумевается сетка 1..4.
        max_col = 4
        cols: list[DashboardColumn] = []
        for col_idx in range(1, max_col + 1):
            col = by_col.get(col_idx) or {"sections": [], "classes": DashboardColumn.classes, "column": col_idx}
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

            cols.append(DashboardColumn(sections=tuple(sections), classes=classes))

        return tuple(cols)

    # Иначе работаем как раньше: порядок в списке = порядок колонок.
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
    app_labels: set[str],
    *,
    label_overrides: dict[tuple[str, str], Any] | None = None,
) -> tuple[DashboardLink, ...]:
    """
    Строит набор линков для app_labels на основе списка моделей из админки.

    Args:
        app_list: Список приложений из `admin.site.get_app_list(request)`.
        app_labels: Множество app_label для отбора моделей.
        label_overrides: Опциональные переопределения заголовков по (app_label, object_name).

    Returns:
        Кортеж `DashboardLink`.
    """
    links: list[DashboardLink] = []
    for app_item in app_list:
        if (app_item.get("app_label") or "") not in app_labels:
            continue
        for m in (app_item.get("models") or []):
            url = m.get("admin_url")
            if url:
                app_label = app_item.get("app_label") or ""
                obj_name = m.get("object_name") or ""
                label = m.get("name", "")
                if label_overrides and (app_label, obj_name) in label_overrides:
                    label = label_overrides[(app_label, obj_name)]
                links.append(DashboardLink(label=label, url=url))
    return tuple(links)


def looks_like_dashboard_layout(raw: Any) -> bool:
    """
    Проверяет формат LUCUS_DASHBOARD вида `[{ "classes": "...", "sections": [...] }, ...]`.

    Args:
        raw: Любое значение из настроек.

    Returns:
        `True`, если формат похож на полный layout-конфиг.
    """
    if not isinstance(raw, (list, tuple)) or not raw:
        return False
    first = raw[0]
    return isinstance(first, dict) and ("classes" in first or "sections" in first)


def looks_like_groups_config(raw: Any) -> bool:
    """
    Проверяет формат конфигурации групп.

    Args:
        raw: Любое значение из настроек.

    Returns:
        `True`, если формат похож на групповой конфиг.
    """
    if not isinstance(raw, (list, tuple)) or not raw:
        return False
    first = raw[0]
    return (
        isinstance(first, dict)
        and "column" in first
        and ("app_labels" in first or "links" in first)
    )


def normalize_group_columns(groups: Iterable[dict[str, Any]]) -> tuple[dict[str, Any], ...]:
    """
    Нормализует поле `column` в группах: ожидается 1-based, значения меньше 1 приводятся к 1.

    Args:
        groups: Итерабельное значение с группами.

    Returns:
        Кортеж групп, где `column` всегда >= 1.
    """
    groups_list = list(groups)
    normalized: list[dict[str, Any]] = []
    for g in groups_list:
        col = int(g.get("column", 1) or 1)
        if col < 1:
            col = 1
        normalized.append({**g, "column": col})
    return tuple(normalized)


def grouped_dashboard_from_app_list(
    request,
    *,
    groups: Iterable[dict[str, Any]] | None = None,
) -> tuple[DashboardColumn, ...]:
    """
    Строит dashboard по списку админских приложений и конфигу групп.

    Args:
        request: Текущий HTTP-запрос (нужен для `admin.site.get_app_list`).
        groups: Опциональные группы конфигурации (иначе берутся из `settings.LUCUS_DASHBOARD`).

    Returns:
        Кортеж колонок dashboard.
    """
    app_list = admin.site.get_app_list(request)

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

    explicit_links_mode = any(g.get("links") for g in groups)

    for g in groups:
        if g.get("links"):
            links: list[DashboardLink] = []
            for link in g.get("links") or []:
                url = link.get("url")
                if not url and link.get("admin_urlname"):
                    url = safe_reverse(link["admin_urlname"])
                if not url:
                    continue
                links.append(DashboardLink(label=link.get("label", ""), url=url))
            links_tuple = tuple(links)
        else:
            app_labels = set(g.get("app_labels") or [])
            links_tuple = links_for_apps(app_list, app_labels, label_overrides=label_overrides)

        if not links_tuple:
            continue

        # column в конфиге 1-based -> индекс в массиве 0-based
        cols[int(g.get("column", 1)) - 1].append(DashboardSection(title=g.get("title", ""), links=links_tuple))

    # Если явно заданы `links`, не добавляем ничего “сверху” автоматически.
    if not explicit_links_mode:
        covered = set().union(*(set(g.get("app_labels") or []) for g in groups))

        for app_item in app_list:
            app_label = (app_item.get("app_label") or "")
            if not app_label or app_label in covered:
                continue
            links = []
            for m in (app_item.get("models") or []):
                url = m.get("admin_url")
                if url:
                    links.append(DashboardLink(label=m.get("name", ""), url=url))
            if links:
                cols[-1].append(DashboardSection(title=app_item.get("name", ""), links=tuple(links)))

    return tuple(DashboardColumn(sections=tuple(secs)) for secs in cols if secs)


def get_dashboard_for_request(request) -> tuple[DashboardColumn, ...]:
    """
    Конфигурация dashboard для admin index.

    Important:
        Настройка переопределяется через `settings.LUCUS_DASHBOARD`.

    Args:
        request: Текущий HTTP-запрос.

    Returns:
        Колонки dashboard.
    """
    raw = getattr(settings, "LUCUS_DASHBOARD", None)

    if raw and looks_like_dashboard_layout(raw):
        # Полная раскладка дашборда (старый/отдельный формат)
        return normalize_config(raw)

    if raw and looks_like_groups_config(raw):
        # Конфигурация групп приложений для карточек на index
        return grouped_dashboard_from_app_list(request, groups=raw)

    return grouped_dashboard_from_app_list(request)

