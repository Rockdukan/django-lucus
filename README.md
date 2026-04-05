# Lucus

[Русский](README.ru.md)

Lucus is a Django package that restyles `django.contrib.admin` with its own `base.html`, layout CSS, and a single bundled admin stylesheet (`lucus/css/lucus-admin.css`) instead of linking the stock admin CSS. Staff can pick a color palette and appearance (light, dark, or system) from the header; choices are stored per user in `LucusAdminUiPreference`. The index page supports a configurable multi-column dashboard.

The default admin navigation sidebar is disabled. On changelist and change-form views, the primary action controls are fixed to the bottom of the viewport so they stay visible while scrolling.

![Admin index — Dune theme, light appearance, full-page background](https://raw.githubusercontent.com/Rockdukan/django-lucus/main/screenshots/screenshot_1.jpg)

*Index page: multi-column dashboard cards (sample apps: Education, Logistics, Support, …), header toolbars for palette, appearance, site, language, and user.*

![Changelist — Slate theme (Instructors)](https://raw.githubusercontent.com/Rockdukan/django-lucus/main/screenshots/screenshot_2.jpg)

*Model changelist: breadcrumbs, search, bulk actions, result table, right-hand filters.*

![Change form — Dracula theme, dark appearance](https://raw.githubusercontent.com/Rockdukan/django-lucus/main/screenshots/screenshot_3.jpg)

*Change form: fieldset, fixed bottom bar (save variants and delete). Capture uses dark mode; palette and appearance are per-user settings.*

## Requirements

- Python 3.10+
- Django `>=5.2,<7` (see `pyproject.toml`)

## Install

```bash
pip install django-lucus
```

The Python package name on PyPI is **django-lucus**; import the app as `lucus`.

## Setup

```python
INSTALLED_APPS = [
    # ...
    "lucus",
    "django.contrib.admin",
]
```

```bash
python manage.py migrate lucus_admin
```

Run `collectstatic` in production so admin assets are served like any other static files.

## Settings

| Setting | Type | Default | Effect |
|---------|------|---------|--------|
| `SITE_NAME` | `str` | `"Site"` | `LUCUS_ADMIN_SITE_HEADER_TEMPLATE` / `site_title` |
| `LUCUS_ADMIN_SITE_HEADER_TEMPLATE` | `str` | `"Administration — {site}"` | `admin.site.site_header` = `.format(site=SITE_NAME)`; use only `{site}` or escape other `{}` |
| `LUCUS_ADMIN_SITE_TITLE_USE_SITE_NAME` | `bool` | `True` | `admin.site.site_title` = `SITE_NAME` if true |
| `LUCUS_ADMIN_BACKGROUND_IMAGE` | `str` / `Path` | `""` | Full-page background: `http(s)://`, `//`, site path `/…`, or static path (no `..`) |
| `LUCUS_ADMIN_BACKGROUND_SCRIM_OPACITY` | `float` | `0.88` | Theme overlay on image, `0.0`…`1.0` |
| `LUCUS_ADMIN_LANGUAGE_SELECTOR` | `bool` | *(auto)* | `False` → hide header language `<select>`. Shown only if `USE_I18N`, `len(LANGUAGES) > 1`, `LocaleMiddleware`, `set_language` URL exists |
| `LUCUS_ADMIN_SITE_SELECTOR` | `bool` | *(auto)* | `False` → hide `django.contrib.sites` header switcher. Shown if sites app + ≥2 `Site` rows |
| `LUCUS_UI` | `dict` | `{}` | See below |
| `LUCUS_EXTRA_STATIC_CSS` | `str` / `list` / `tuple` | `()` | Extra CSS paths after palette; no `..`, no leading `/` |
| `LUCUS_EMPTY_VALUE_DISPLAY_WRAP` | `bool` | `True` | Wrap empty changelist cells in `lucus-admin-empty` |
| `LUCUS_EMPTY_VALUE_PLACEHOLDER` | `str` | `"—"` | `empty_value_display` text |
| `LUCUS_ACTIONS_ON_BOTTOM` | `bool` | `True` | Set `ModelAdmin.actions_on_bottom` on the class |
| `LUCUS_ACTIONS_ON_TOP` | `bool` | `True` | Set `ModelAdmin.actions_on_top` on the class |
| `LUCUS_DASHBOARD` | `list` / `None` | `None` | Dashboard; `None` → built-in grouped layout |
| `LUCUS_DASHBOARD_APPEND_UNCOVERED` | `bool` | `True` | Grouped mode: append uncovered apps to last column |

**Palette / appearance:** not in `settings`. Stored per user in `LucusAdminUiPreference`. Slugs: `olivia`, `grey`, `slate`, `dune`, `midnight`, `nord`, `dracula`, `github`, `catppuccin`, `tokyo` → `lucus/static/lucus/css/<slug>.css`. Context: `lucus.theme.lucus_admin_extra_context` → `admin.site.each_context`.

### `LUCUS_UI`

| Key | Default | Effect |
|-----|---------|--------|
| `help_as_icon` | `True` | Field `help_text` behind a `?` / `<details>` |
| `high_contrast_toggle` | `False` | User menu “High contrast” (`localStorage` + `data-lucus-contrast` on `<html>`) |

```python
LUCUS_UI = {
    "help_as_icon": True,
    "high_contrast_toggle": False,
}
```

## `LUCUS_DASHBOARD`

Context: `lucus_dashboard_columns` from `get_dashboard_for_request`. Section link: `{"label", "url"}` or `{"label", "admin_urlname"}` (e.g. `admin:app_model_changelist`). Section omitted if no link resolves.

**Layout mode:** `[{ "column"?: 1–4, "classes"?: str, "sections": [{ "title", "links": [...] }] }, …]`. Same `column` → merge sections; `classes` from first dict.

**Groups mode:** `[{ "column", "title", "links"?: [...], "app_labels"?: set|list|tuple|frozenset }, …]`. `links` first, then models from `app_labels`; duplicate URLs dropped. `list`/`tuple` `app_labels` → order kept; `set` → `get_app_list` order.

`LUCUS_DASHBOARD_APPEND_UNCOVERED`: `True` → apps not referenced by groups / inferred from `admin_urlname` go to last column; `False` → only configured groups.

```python
LUCUS_DASHBOARD = [
    {
        "column": 1,
        "classes": "lucus-dashboard__col lucus-col lucus-col-3 lucus-col-md-6 lucus-col-sm-12",
        "sections": [
            {
                "title": "Education",
                "links": [
                    {"label": "Instructors", "admin_urlname": "admin:academy_instructor_changelist"},
                    {"label": "Courses", "url": "/admin/academy/course/"},
                ],
            },
        ],
    },
]
```

```python
LUCUS_DASHBOARD = [
    {"column": 1, "title": "Authorization", "app_labels": {"auth"}},
]
```

```python
LUCUS_DASHBOARD = [
    {
        "column": 2,
        "title": "Auth",
        "links": [{"label": "Users", "admin_urlname": "admin:auth_user_changelist"}],
        "app_labels": ("auth",),
    },
]
```

## Stylesheets

Stylesheets load in this order: `lucus/css/style.css`, `lucus/css/lucus-admin.css`, the selected palette `lucus/css/<slug>.css`, then paths from `LUCUS_EXTRA_STATIC_CSS`. JavaScript for admin widgets, inlines, and actions still comes from `django.contrib.admin`.

To add a custom palette, ship `lucus/css/<slug>.css` on your static path and append the slug and label to `lucus.theme.BUNDLED_COLOR_SCHEMES` in your project.

## Modules

| Module | Responsibility |
|--------|----------------|
| `lucus.apps.LucusConfig` | `ready()`: `site_header` / `site_title`, `each_context` hook, dashboard context, routes `lucus_save_ui` and `lucus_save_site`, `enable_nav_sidebar = False`, `empty_value_display`, `ModelAdmin` actions placement |
| `lucus.dashboard` | Normalizes `LUCUS_DASHBOARD` into column structures |
| `lucus.models` | `LucusAdminUiPreference` (palette + appearance per user) |
| `lucus.theme` | Bundled schemes, `lucus_admin_extra_context(request)` |
| `lucus.views` | POST handlers for saving UI and site selection |

Package version: `lucus.__version__`.

If you use the optional sites switcher in the header and need `request.site` inside `/admin/` to match the selection, register `lucus.sites_panel.LucusAdminSiteMiddleware` immediately after `SessionMiddleware` (see `lucus.sites_panel`).

Supported Django versions are declared in `pyproject.toml` (currently 5.2 and compatible 6.x).
