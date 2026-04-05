# Lucus (Django admin theme)

[Русский](README.ru.md)

Admin skin: Lucus `base.html`, bundled CSS (`lucus/css/style.css`, `lucus-admin.css`), per-user palette + light/dark/auto (`LucusAdminUiPreference`), `/admin/` dashboard config. Nav sidebar off; changelist actions + change-form save row pinned to viewport bottom.

![Lucus](https://raw.githubusercontent.com/Rockdukan/django-lucus/main/screenshots/screenshot_1.jpg)
![Lucus](https://raw.githubusercontent.com/Rockdukan/django-lucus/main/screenshots/screenshot_2.jpg)
![Lucus](https://raw.githubusercontent.com/Rockdukan/django-lucus/main/screenshots/screenshot_3.jpg)

## Requirements

- Python 3.10+
- Django `>=5.2,<7` (see `pyproject.toml`)

## Install

```bash
pip install django-lucus
```

Import: `lucus`. PyPI: **django-lucus**.

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

Production: `collectstatic` as usual.

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

Example:

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

## Static

Load order: `lucus/css/style.css` → `lucus/css/lucus-admin.css` → `lucus/css/<slug>.css` → `LUCUS_EXTRA_STATIC_CSS`. Admin widget JS still from `django.contrib.admin`.

Custom palette: add `static/.../lucus/css/<slug>.css` and extend `lucus.theme.BUNDLED_COLOR_SCHEMES` in your project.

## Package

- `lucus.apps.LucusConfig` — `ready()`: headers, `each_context`, dashboard, URLs `lucus_save_ui` / `lucus_save_site`, `enable_nav_sidebar = False`, empty value display, actions flags
- `lucus.dashboard` — config → columns
- `lucus.models` — `LucusAdminUiPreference`
- `lucus.theme` — schemes, `lucus_admin_extra_context`
- `lucus.views` — POST save UI / site

Version: `lucus.__version__`.

**Sites toolbar:** for `request.site` in admin to follow the header switcher, add `lucus.sites_panel.LucusAdminSiteMiddleware` after `SessionMiddleware` (`lucus.sites_panel`).

**Compatibility:** Django 5.2+ (`pyproject.toml`).
